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

    // New Visuals Elements
    const resChart = document.getElementById("res-chart");
    const scoreFh = document.getElementById("res-score-fh");
    const scorePr = document.getElementById("res-score-pr");
    const scoreVa = document.getElementById("res-score-va");
    const scoreRi = document.getElementById("res-score-ri");

    // Sentiment Elements
    const sentLabel = document.getElementById("res-sentiment-label");
    const sentScore = document.getElementById("res-sentiment-score");
    const sentHeadlines = document.querySelector("#res-headlines ul");

    // Forensics Elements
    const resDcfPrice = document.getElementById("res-dcf-price");
    const resDcfUpside = document.getElementById("res-dcf-upside");
    const resPiotroski = document.getElementById("res-piotroski");
    const resAltman = document.getElementById("res-altman");
    const resAltmanZone = document.getElementById("res-altman-zone");

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
        // Show Results section FIRST so that TradingView Canvas has >0 dimensions!
        resultsSection.classList.remove("hidden");

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
        // Render Interactive Price Chart
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

        // Populate Sentiment
        if (data.sentiment) {
            sentLabel.textContent = data.sentiment.sentiment_label;
            sentScore.textContent = `Score: ${data.sentiment.average_polarity}`;

            // Apply verdict styling format to sentiment
            sentLabel.className = "";
            const sentClass = data.sentiment.sentiment_label.toLowerCase().replace(" ", "-");
            if (sentClass === "bullish") sentLabel.style.color = "#2ea043";
            else if (sentClass === "bearish") sentLabel.style.color = "#f85149";
            else sentLabel.style.color = "#d29922";

            sentHeadlines.innerHTML = "";
            if (data.sentiment.headlines) {
                data.sentiment.headlines.forEach(news => {
                    const li = document.createElement("li");
                    li.style.fontSize = "0.85rem";
                    li.style.marginBottom = "10px";
                    li.style.lineHeight = "1.4";

                    const a = document.createElement("a");
                    a.href = news.url;
                    a.target = "_blank";
                    const polarityTag = news.polarity > 0 ? `[+${news.polarity}]` : `[${news.polarity}]`;
                    a.textContent = `${news.date} ${polarityTag} - ${news.title}`;
                    a.style.color = "inherit";
                    a.style.textDecoration = "none";

                    // Hover effect
                    a.addEventListener('mouseenter', () => a.style.color = '#58a6ff');
                    a.addEventListener('mouseleave', () => a.style.color = 'inherit');

                    li.appendChild(a);
                    sentHeadlines.appendChild(li);
                });
            }
        }

        // Populate Forensics
        if (data.forensics) {
            const f = data.forensics;
            if (f.dcf && f.dcf.is_valid) {
                resDcfPrice.textContent = `$${f.dcf.target_price}`;
                const up = (f.dcf.upside * 100).toFixed(2);
                resDcfUpside.textContent = `${up > 0 ? '+' : ''}${up}% Margin of Safety`;
                if (f.dcf.upside > 0) {
                    resDcfUpside.style.color = "#2ea043";
                } else {
                    resDcfUpside.style.color = "#f85149";
                }
            } else {
                resDcfPrice.textContent = "N/A";
                resDcfUpside.textContent = "Insufficient FCF Data";
                resDcfUpside.style.color = "#8b949e";
            }
            resPiotroski.textContent = `${f.piotroski_f_score}/9`;

            if (f.altman_z_score) {
                resAltman.textContent = f.altman_z_score.score;
                resAltmanZone.textContent = f.altman_z_score.risk_zone;
                if (f.altman_z_score.risk_zone === "Safe") resAltmanZone.style.color = "#2ea043";
                else if (f.altman_z_score.risk_zone === "Distress") resAltmanZone.style.color = "#f85149";
                else resAltmanZone.style.color = "#d29922";
            }
        }

        // Radar Chart (Sub-Scores)
        if (data.sub_scores) {
            if (window.radarChartInstance) {
                window.radarChartInstance.destroy();
            }
            const ctx = document.getElementById('radarChart').getContext('2d');
            window.radarChartInstance = new Chart(ctx, {
                type: 'radar',
                data: {
                    labels: ['Financial Health', 'Profitability', 'Valuation', 'Risk'],
                    datasets: [{
                        label: 'ONYX Sub-Scores',
                        data: [
                            data.sub_scores.financial_health || 0,
                            data.sub_scores.profitability || 0,
                            data.sub_scores.valuation || 0,
                            data.sub_scores.risk || 0
                        ],
                        backgroundColor: 'rgba(88, 166, 255, 0.2)',
                        borderColor: 'rgba(88, 166, 255, 1)',
                        pointBackgroundColor: 'rgba(88, 166, 255, 1)',
                        pointBorderColor: '#fff',
                        pointHoverBackgroundColor: '#fff',
                        pointHoverBorderColor: 'rgba(88, 166, 255, 1)'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        r: {
                            angleLines: { color: 'rgba(255, 255, 255, 0.1)' },
                            grid: { color: 'rgba(255, 255, 255, 0.1)' },
                            pointLabels: { color: '#8b949e', font: { family: 'Inter', size: 12 } },
                            ticks: { display: false, min: 0, max: 100 }
                        }
                    },
                    plugins: {
                        legend: { display: false }
                    }
                }
            });
        }

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
