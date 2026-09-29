/* =========================================
   TRIPBUDDY AI
   Frontend Controller
========================================= */


/* =========================================
   DOM ELEMENTS
========================================= */

const tripForm = document.getElementById("trip-form");

const tripRequest = document.getElementById("trip-request");

const characterCount =
    document.getElementById("character-count");

const generateButton =
    document.getElementById("generate-button");

const loadingSection =
    document.getElementById("loading-section");

const resultsSection =
    document.getElementById("results-section");

const progressBar =
    document.getElementById("progress-bar");

const loadingMessage =
    document.getElementById("loading-message");

const toast =
    document.getElementById("toast");

const toastMessage =
    document.getElementById("toast-message");


/* =========================================
   CHARACTER COUNTER
========================================= */

if (tripRequest) {

    tripRequest.addEventListener("input", () => {

        const count = tripRequest.value.length;

        characterCount.textContent =
            `${count.toLocaleString()} characters`;

    });

}


/* =========================================
   FOCUS PLANNER
========================================= */

function focusPlanner() {

    const planner =
        document.getElementById("planner");

    planner.scrollIntoView({
        behavior: "smooth",
        block: "center"
    });

    setTimeout(() => {
        tripRequest.focus();
    }, 600);

}


/* =========================================
   QUICK PROMPTS
========================================= */

function usePrompt(prompt) {

    tripRequest.value = prompt;

    tripRequest.dispatchEvent(
        new Event("input")
    );

    focusPlanner();

}


/* =========================================
   CLEAR PLANNER
========================================= */

function clearPlanner() {

    tripRequest.value = "";

    tripRequest.dispatchEvent(
        new Event("input")
    );

    tripRequest.focus();

}


/* =========================================
   TOAST
========================================= */

let toastTimer = null;

function showToast(message) {

    toastMessage.textContent = message;

    toast.classList.add("show");

    clearTimeout(toastTimer);

    toastTimer = setTimeout(() => {

        toast.classList.remove("show");

    }, 3500);

}


/* =========================================
   LOADING STATE
========================================= */

let loadingTimer = null;

function startLoadingAnimation() {

    let progress = 10;

    progressBar.style.width = "10%";

    const agents = [
        document.getElementById("agent-flight"),
        document.getElementById("agent-hotel"),
        document.getElementById("agent-itinerary")
    ];

    const messages = [
        "Searching the best flight routes...",
        "Finding suitable hotels and stays...",
        "Building your personalized itinerary...",
        "Putting everything together..."
    ];

    let step = 0;

    loadingMessage.textContent =
        messages[0];

    loadingTimer = setInterval(() => {

        step++;

        progress =
            Math.min(
                90,
                progress + 20
            );

        progressBar.style.width =
            `${progress}%`;

        if (step === 1) {

            agents[0].classList.add("done");

            agents[1].classList.add("active");

            loadingMessage.textContent =
                messages[1];

        }

        if (step === 2) {

            agents[1].classList.add("done");

            agents[2].classList.add("active");

            loadingMessage.textContent =
                messages[2];

        }

        if (step >= 3) {

            loadingMessage.textContent =
                messages[3];

        }

    }, 1800);

}


function stopLoadingAnimation() {

    clearInterval(loadingTimer);

    progressBar.style.width = "100%";

}


/* =========================================
   SHOW / HIDE SECTIONS
========================================= */

function showLoading() {

    resultsSection.classList.add("hidden");

    loadingSection.classList.remove("hidden");

    loadingSection.scrollIntoView({
        behavior: "smooth",
        block: "center"
    });

    startLoadingAnimation();

}


function hideLoading() {

    loadingSection.classList.add("hidden");

}


/* =========================================
   FORMAT AI RESPONSE
========================================= */

function formatResponse(text) {

    if (!text) {
        return "No information available.";
    }

    let html = escapeHtml(text);

    /*
        Convert Markdown-style formatting
        into simple HTML.
    */

    html = html.replace(
        /\*\*(.*?)\*\*/g,
        "<strong>$1</strong>"
    );

    html = html.replace(
        /^### (.*?)$/gm,
        "<h4>$1</h4>"
    );

    html = html.replace(
        /^## (.*?)$/gm,
        "<h3>$1</h3>"
    );

    html = html.replace(
        /^# (.*?)$/gm,
        "<h2>$1</h2>"
    );

    html = html.replace(
        /^- (.*?)$/gm,
        "• $1"
    );

    html = html.replace(
        /\n/g,
        "<br>"
    );

    return html;
}


/* =========================================
   HTML ESCAPE
========================================= */

function escapeHtml(value) {

    const div =
        document.createElement("div");

    div.textContent = value;

    return div.innerHTML;

}


let latestTripData = null;


/* =========================================
   DISPLAY RESULTS
========================================= */

function displayResults(data) {

    const summary =
        document.getElementById("trip-summary");

    const flights =
        document.getElementById("flight-results");

    const hotels =
        document.getElementById("hotel-results");

    const itinerary =
        document.getElementById("itinerary-results");

    const finalResponse =
        document.getElementById("final-response");


    /*
        Summary
    */

    summary.innerHTML =
        formatResponse(
            extractSummary(data)
        );


    /*
        Flights
    */

    flights.innerHTML =
        formatResponse(
            data.flight_results ||
            "No flight information was returned."
        );


    /*
        Hotels
    */

    hotels.innerHTML =
        formatResponse(
            data.hotel_results ||
            "No hotel information was returned."
        );


    /*
        Itinerary
    */

    itinerary.innerHTML =
        formatResponse(
            data.itinerary ||
            "No itinerary was generated."
        );


    /*
        Final AI Response
    */

    finalResponse.innerHTML =
        formatResponse(
            data.answer ||
            "No final response was generated."
        );


    /*
        Show results
    */

    resultsSection.classList.remove(
        "hidden"
    );

    resultsSection.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });

}


/* =========================================
   EXTRACT SUMMARY
========================================= */

function extractSummary(data) {

    /*
        If backend eventually returns
        structured trip metadata, use it.
    */

    if (data.summary) {
        return data.summary;
    }

    /*
        Otherwise create a simple
        summary from the user request.
    */

    const request =
        data.user_query ||
        tripRequest.value;

    if (!request) {

        return "Your personalized travel plan is ready.";

    }

    return (
        `Trip request received:\n\n${request}\n\n` +
        `TripBuddy AI has generated flight information, ` +
        `hotel suggestions and a day-by-day itinerary.`
    );

}


/* =========================================
   FORM SUBMISSION
========================================= */

if (tripForm) {

    tripForm.addEventListener(
        "submit",
        async (event) => {

            event.preventDefault();

            const query = tripRequest.value.trim();

            if (!query) {

                showToast(
                    "Please describe your trip first."
                );

                tripRequest.focus();

                return;
            }

            generateButton.disabled = true;

            const buttonText =
                generateButton.querySelector(".button-text");

            if (buttonText) {
                buttonText.textContent = "Planning...";
            }

            showLoading();

            try {

                console.log("🚀 Sending request to /api/plan...");
                console.log("📝 Query:", query);

                const response = await fetch(
                    "/api/plan",
                    {
                        method: "POST",

                        headers: {
                            "Content-Type": "application/json"
                        },

                        body: JSON.stringify({
                            message: query
                        })
                    }
                );

                console.log(
                    "📡 API status:",
                    response.status
                );

                if (!response.ok) {

                    let errorMessage =
                        `Server error (${response.status})`;

                    try {

                        const errorData =
                            await response.json();

                        console.error(
                            "❌ API error:",
                            errorData
                        );

                        if (errorData.error) {
                            errorMessage =
                                errorData.error;
                        }

                    } catch (jsonError) {

                        console.error(
                            "Could not parse error response:",
                            jsonError
                        );
                    }

                    throw new Error(errorMessage);
                }

                const data =
                    await response.json();

                latestTripData = data;

                console.log(
                    "✅ API response received:",
                    data
                );

                /*
                    Validate response
                */

                if (!data) {
                    throw new Error(
                        "The server returned an empty response."
                    );
                }

                /*
                    Stop loading BEFORE displaying results
                */

                hideLoading();

                /*
                    Display results
                */

                console.log(
                    "🎯 Displaying results..."
                );

                displayResults(data);

                console.log(
                    "✅ Results displayed successfully."
                );

            } catch (error) {

                console.error(
                    "❌ TripBuddy error:",
                    error
                );
                
                hideLoading();
                showToast(
                    error.message ||
                    "Something went wrong. Please try again."
                );

            } finally {

                generateButton.disabled = false;

                if (buttonText) {
                    buttonText.textContent =
                        "Plan My Trip";
                }

            }

        }
    );

}



/* =========================================
   NEW TRIP
========================================= */

function newTrip() {

    latestTripData = null;

    resultsSection.classList.add(
        "hidden"
    );

    tripRequest.value = "";

    tripRequest.dispatchEvent(
        new Event("input")
    );

    focusPlanner();

}


/* =========================================
   KEYBOARD SHORTCUT
========================================= */

document.addEventListener(
    "keydown",
    (event) => {

        /*
            Cmd/Ctrl + Enter
            submits the planner.
        */

        if (
            (event.metaKey || event.ctrlKey) &&
            event.key === "Enter"
        ) {

            if (
                document.activeElement ===
                tripRequest
            ) {

                tripForm.requestSubmit();

            }

        }

    }
);


/* =========================================
   INITIALIZATION
========================================= */

document.addEventListener(
    "DOMContentLoaded",
    () => {

        console.log(
            "✈ TripBuddy AI frontend loaded."
        );

    }
);


/* =========================================
   PDF DOWNLOAD
========================================= */



async function downloadTripPDF() {

    if (!latestTripData) {

        showToast(
            "Please generate a trip plan first."
        );

        return;
    }

    const downloadButton =
        document.getElementById("download-pdf-button");

    if (!downloadButton) {
        console.error(
            "PDF download button was not found."
        );
        return;
    }

    const originalText =
        downloadButton.innerHTML;

    try {

        downloadButton.disabled = true;

        downloadButton.innerHTML =
            "⏳ Generating PDF...";

        const response = await fetch(
            "/api/download-pdf",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify(
                    latestTripData
                )
            }
        );

        if (!response.ok) {

            let errorMessage =
                `PDF generation failed (${response.status})`;

            try {

                const errorData =
                    await response.json();

                if (errorData.error) {
                    errorMessage =
                        errorData.error;
                }

            } catch (jsonError) {

                console.error(
                    "Could not parse PDF error:",
                    jsonError
                );

            }

            throw new Error(errorMessage);
        }

        const blob =
            await response.blob();

        const url =
            window.URL.createObjectURL(blob);

        const link =
            document.createElement("a");

        link.href = url;
        link.download =
            "TripBuddy_Travel_Plan.pdf";

        document.body.appendChild(link);

        link.click();

        link.remove();

        window.URL.revokeObjectURL(url);

        showToast(
            "Trip PDF downloaded successfully."
        );

    } catch (error) {

        console.error(
            "❌ PDF download error:",
            error
        );

        showToast(
            error.message ||
            "Unable to generate the PDF."
        );

    } finally {

        downloadButton.disabled = false;

        downloadButton.innerHTML =
            originalText;
    }
}
