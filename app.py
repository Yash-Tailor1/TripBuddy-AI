from pathlib import Path
import html
import re
import traceback
from io import BytesIO

import uvicorn

from fastapi import FastAPI, Request
from fastapi.responses import (
    HTMLResponse,
    JSONResponse,
    StreamingResponse,
)
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)

from backend import run_travel_agent


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

TEMPLATES_DIR = BASE_DIR / "Templates"
STATIC_DIR = BASE_DIR / "Static"


# ============================================================
# FASTAPI
# ============================================================

app = FastAPI(
    title="AI Travel Planning System",
    description="LangGraph Multi-Agent Travel Planner with FastAPI Frontend",
    version="1.0.0",
)


# ============================================================
# STATIC FILES
# ============================================================

app.mount(
    "/static",
    StaticFiles(directory=str(STATIC_DIR)),
    name="static",
)


# ============================================================
# TEMPLATES
# ============================================================

templates = Jinja2Templates(
    directory=str(TEMPLATES_DIR)
)


# ============================================================
# REQUEST MODELS
# ============================================================

class TravelRequest(BaseModel):
    message: str
    thread_id: str | None = None


class PDFRequest(BaseModel):
    user_query: str = ""
    answer: str = ""
    flight_results: str = ""
    hotel_results: str = ""
    itinerary: str = ""


# ============================================================
# PDF HELPERS
# ============================================================

PDF_FONT = "Helvetica"
PDF_BOLD_FONT = "Helvetica-Bold"


def setup_pdf_fonts():
    """
    Use a Unicode font when one is available so characters such as
    ₹ render correctly. Fall back to ReportLab's built-in fonts.
    """

    global PDF_FONT, PDF_BOLD_FONT

    candidates = [
        (
            "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
            "TripBuddyUnicode",
        ),
        (
            "/Library/Fonts/Arial Unicode.ttf",
            "TripBuddyUnicode",
        ),
        (
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "TripBuddyUnicode",
        ),
    ]

    for font_path, font_name in candidates:

        path = Path(font_path)

        if not path.exists():
            continue

        try:

            pdfmetrics.registerFont(
                TTFont(font_name, str(path))
            )

            PDF_FONT = font_name

            bold_candidates = [
                path.with_name("DejaVuSans-Bold.ttf"),
                Path(
                    "/System/Library/Fonts/Supplemental/"
                    "Arial Bold.ttf"
                ),
                Path("/Library/Fonts/Arial Bold.ttf"),
            ]

            for bold_path in bold_candidates:

                if bold_path.exists():

                    try:

                        pdfmetrics.registerFont(
                            TTFont(
                                f"{font_name}Bold",
                                str(bold_path),
                            )
                        )

                        PDF_BOLD_FONT = f"{font_name}Bold"
                        return

                    except Exception:
                        pass

            PDF_BOLD_FONT = PDF_FONT
            return

        except Exception:
            continue


setup_pdf_fonts()


def clean_pdf_text(value: str) -> str:
    """
    Convert Markdown-ish AI output into readable PDF text.
    HTML is escaped later before being passed to ReportLab.
    """

    if not value:
        return ""

    text = value.replace("\r\n", "\n").replace("\r", "\n")

    # Markdown links: [label](url) -> label (url)
    text = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        r"\1 (\2)",
        text,
    )

    # Remove Markdown emphasis markers while keeping the text.
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"__(.*?)__", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)

    return text.strip()


def add_pdf_section(
    story,
    heading: str,
    content: str,
    styles,
):
    content = clean_pdf_text(content)

    if not content:
        return

    story.append(
        Paragraph(
            html.escape(heading),
            styles["TripHeading"],
        )
    )

    for line in content.split("\n"):

        line = line.strip()

        if not line:
            story.append(Spacer(1, 3 * mm))
            continue

        # Convert simple Markdown headings to visual headings.
        heading_match = re.match(
            r"^#{1,3}\s+(.*)$",
            line,
        )

        if heading_match:

            heading_text = heading_match.group(1).strip()

            story.append(
                Paragraph(
                    html.escape(heading_text),
                    styles["TripSubheading"],
                )
            )

            continue

        safe_line = html.escape(line)

        story.append(
            Paragraph(
                safe_line,
                styles["TripBody"],
            )
        )

        story.append(Spacer(1, 1.5 * mm))

    story.append(Spacer(1, 4 * mm))


# ============================================================
# HOME PAGE
# ============================================================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={},
    )


# ============================================================
# TRAVEL API
# ============================================================

@app.post("/api/plan")
async def travel_planner(request_data: TravelRequest):

    try:

        user_message = request_data.message.strip()

        if not user_message:

            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": "Message cannot be empty.",
                },
            )

        result = run_travel_agent(
            user_input=user_message,
            thread_id=request_data.thread_id,
        )

        return JSONResponse(
            content={
                "success": True,
                "thread_id": result.get("thread_id"),
                "answer": result.get("answer", ""),
                "flight_results": result.get(
                    "flight_results", ""
                ),
                "hotel_results": result.get(
                    "hotel_results", ""
                ),
                "itinerary": result.get(
                    "itinerary", ""
                ),
                "llm_calls": result.get(
                    "llm_calls", 0
                ),
                "user_query": user_message,
            }
        )

    except Exception as e:

        print("\n" + "=" * 60)
        print("TRIPBUDDY API ERROR")
        print("=" * 60)

        print("ERROR:", e)

        traceback.print_exc()

        print("=" * 60 + "\n")

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e),
            },
        )


# ============================================================
# PDF DOWNLOAD
# ============================================================

@app.post("/api/download-pdf")
async def download_pdf(request_data: PDFRequest):

    try:

        buffer = BytesIO()

        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=18 * mm,
            leftMargin=18 * mm,
            topMargin=18 * mm,
            bottomMargin=18 * mm,
            title="TripBuddy AI Travel Plan",
            author="TripBuddy AI",
        )

        base_styles = getSampleStyleSheet()

        styles = {
            "TripTitle": ParagraphStyle(
                "TripTitle",
                parent=base_styles["Title"],
                fontName=PDF_BOLD_FONT,
                fontSize=22,
                leading=27,
                textColor=colors.HexColor("#111827"),
                alignment=TA_LEFT,
                spaceAfter=5 * mm,
            ),
            "TripSubtitle": ParagraphStyle(
                "TripSubtitle",
                parent=base_styles["Normal"],
                fontName=PDF_FONT,
                fontSize=9,
                leading=13,
                textColor=colors.HexColor("#6B7280"),
                spaceAfter=7 * mm,
            ),
            "TripHeading": ParagraphStyle(
                "TripHeading",
                parent=base_styles["Heading2"],
                fontName=PDF_BOLD_FONT,
                fontSize=14,
                leading=18,
                textColor=colors.HexColor("#4F46E5"),
                spaceBefore=3 * mm,
                spaceAfter=3 * mm,
            ),
            "TripSubheading": ParagraphStyle(
                "TripSubheading",
                parent=base_styles["Heading3"],
                fontName=PDF_BOLD_FONT,
                fontSize=11,
                leading=15,
                textColor=colors.HexColor("#111827"),
                spaceBefore=2 * mm,
                spaceAfter=2 * mm,
            ),
            "TripBody": ParagraphStyle(
                "TripBody",
                parent=base_styles["BodyText"],
                fontName=PDF_FONT,
                fontSize=9.5,
                leading=14,
                textColor=colors.HexColor("#374151"),
                spaceAfter=1 * mm,
            ),
        }

        story = []

        story.append(
            Paragraph(
                "TripBuddy AI — Travel Plan",
                styles["TripTitle"],
            )
        )

        story.append(
            Paragraph(
                "Your AI-generated travel plan",
                styles["TripSubtitle"],
            )
        )

        if request_data.user_query:

            add_pdf_section(
                story,
                "Travel Request",
                request_data.user_query,
                styles,
            )

        add_pdf_section(
            story,
            "Flight Information",
            request_data.flight_results,
            styles,
        )

        add_pdf_section(
            story,
            "Hotel Suggestions",
            request_data.hotel_results,
            styles,
        )

        add_pdf_section(
            story,
            "Day-by-Day Itinerary",
            request_data.itinerary,
            styles,
        )

        add_pdf_section(
            story,
            "TripBuddy AI Travel Plan",
            request_data.answer,
            styles,
        )

        if not story:

            story.append(
                Paragraph(
                    "No trip information was available.",
                    styles["TripBody"],
                )
            )

        doc.build(story)

        buffer.seek(0)

        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition":
                    "attachment; filename=TripBuddy_Travel_Plan.pdf"
            },
        )

    except Exception as e:

        print("\n" + "=" * 60)
        print("TRIPBUDDY PDF ERROR")
        print("=" * 60)

        print("ERROR:", e)

        traceback.print_exc()

        print("=" * 60 + "\n")

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": f"PDF generation failed: {e}",
            },
        )


# ============================================================
# OLD API ROUTE
# ============================================================

@app.post("/api/travel")
async def travel_planner_legacy(
    request_data: TravelRequest,
):

    return await travel_planner(request_data)


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
async def health_check():

    return {
        "status": "ok",
        "message": "AI Travel Planner API is running",
    }


# ============================================================
# FAVICON
# ============================================================

@app.get("/favicon.ico")
async def favicon():

    return JSONResponse(content={})


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":

    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
