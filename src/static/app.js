document.addEventListener("DOMContentLoaded", () => {
    const tickerInput = document.getElementById("ticker-input");
    const generateBtn = document.getElementById("generate-btn");
    const searchSection = document.getElementById("search-section");
    const progressContainer = document.getElementById("progress-container");
    const progressTicker = document.getElementById("progress-ticker");
    const resultsSection = document.getElementById("results-section");
    const newSearchBtn = document.getElementById("new-search-btn");
    const downloadBtn = document.getElementById("download-btn");

    // Results Elements
    const resTicker = document.getElementById("res-ticker");
    const resScore = document.getElementById("res-score");
    const resLabel = document.getElementById("res-label");
    const resPositive = document.querySelector("#res-positive ul");
    const resNegative = document.querySelector("#res-negative ul");

    // New Visuals Elements
    const resChart = document.getElementById("res-chart");
    const scoreFh = document.getElementById("res-score-fh");
    const scorePr = document.getElementById("res-score-pr");
    const scoreVa = document.getElementById("res-score-va");
    const scoreRi = document.getElementById("res-score-ri");

    let currentTicker = "";

    // Allow Enter key to submit
    tickerInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") {
            generateBtn.click();
        }
    });

    generateBtn.addEventListener("click", async () => {
        const query = tickerInput.value.trim().toUpperCase();
        if (!query) return;

        currentTicker = query;
        startAnalysis(query);
    });

    newSearchBtn.addEventListener("click", () => {
        resetUI();
    });

    downloadBtn.addEventListener("click", () => {
        window.location.href = `/api/download/${currentTicker}`;
    });

    async function startAnalysis(ticker) {
        // UI State transition
        generateBtn.disabled = true;
        progressTicker.textContent = ticker;
        progressContainer.classList.remove("hidden");

        // Mock progress steps over time
        const steps = [
            document.getElementById("step-data"),
            document.getElementById("step-ml"),
            document.getElementById("step-pdf"),
        ];

        // Reset steps
        steps.forEach(s => { s.classList.remove("active", "completed"); s.classList.add("pending"); });

        // Step 1: Data Fetching
        steps[0].classList.add("active");

        try {
            // Call API
            const response = await fetch("/api/analyze", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ ticker: ticker })
            });

            // Step 1 complete, Step 2 active
            steps[0].classList.replace("active", "completed");
            steps[1].classList.replace("pending", "active");

            const data = await response.json();

            if (!response.ok) {
                alert("Error analyzing company: " + (data.detail || "Unknown error"));
                resetUI();
                return;
            }

            // Step 2 complete, Step 3 active (Fake delay for UI effect)
            setTimeout(() => {
                steps[1].classList.replace("active", "completed");
                steps[2].classList.replace("pending", "active");

                // Step 3 complete -> Show results
                setTimeout(() => {
                    steps[2].classList.replace("active", "completed");
                    showResults(data);
                }, 800);
            }, 800);

        } catch (err) {
            console.error(err);
            alert("Network error occurred.");
            resetUI();
        }
    }

    function showResults(data) {
        // Hide Search UI entirely
        searchSection.classList.add("hidden");
        // Update DOM
        resTicker.textContent = data.ticker;

        // Animate primary score
        animateValue(resScore, 0, data.onyx_score, 1000);

        // Populate Subscores
        const sub = data.sub_scores || {};
        animateValue(scoreFh, 0, sub.financial_health || 0, 800);
        animateValue(scorePr, 0, sub.profitability || 0, 800);
        animateValue(scoreVa, 0, sub.valuation || 0, 800);
        animateValue(scoreRi, 0, sub.risk || 0, 800);

        // Render Chart
        if (data.chart_b64) {
            resChart.src = data.chart_b64;
            resChart.parentElement.classList.remove("hidden");
        } else {
            resChart.parentElement.classList.add("hidden");
        }

        resLabel.textContent = data.verdict;

        // Remove existing classes
        resLabel.className = "verdict-label";
        // Apply verdict styling format
        const verdictClass = data.verdict.toLowerCase().replace(" ", "-");
        resLabel.classList.add(verdictClass);

        // Populate lists
        resPositive.innerHTML = "";
        if (data.top_drivers) {
            data.top_drivers.forEach(sig => {
                const li = document.createElement("li");
                li.textContent = sig;
                resPositive.appendChild(li);
            });
        }

        // Show Results
        resultsSection.classList.remove("hidden");
    }

    function resetUI() {
        tickerInput.value = "";
        generateBtn.disabled = false;
        searchSection.classList.remove("hidden");
        progressContainer.classList.add("hidden");
        resultsSection.classList.add("hidden");
        tickerInput.focus();
    }

    function animateValue(obj, start, end, duration) {
        let startTimestamp = null;
        const step = (timestamp) => {
            if (!startTimestamp) startTimestamp = timestamp;
            const progress = Math.min((timestamp - startTimestamp) / duration, 1);
            obj.innerHTML = Math.floor(progress * (end - start) + start);
            if (progress < 1) {
                window.requestAnimationFrame(step);
            }
        };
        window.requestAnimationFrame(step);
    }
});
