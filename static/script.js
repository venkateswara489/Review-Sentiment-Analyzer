document.addEventListener('DOMContentLoaded', () => {
    const analyzeBtn = document.getElementById('analyzeBtn');
    const reviewInput = document.getElementById('reviewInput');
    const resultsContainer = document.getElementById('resultsContainer');
    const emptyState = document.getElementById('emptyState');
    const sentimentBadge = document.getElementById('sentimentBadge');
    const sentimentText = document.getElementById('sentimentText');
    const aspectsGrid = document.getElementById('aspectsGrid');
    const totalReviewsEl = document.getElementById('totalReviews');
    let aspectChart = null;
    let totalReviews = 0;

    // Sample reviews click handlers
    document.querySelectorAll('.sample-item').forEach(item => {
        item.addEventListener('click', () => {
            const sampleText = item.dataset.sample;
            reviewInput.value = sampleText;
            reviewInput.focus();
        });
    });

    analyzeBtn.addEventListener('click', async () => {
        const text = reviewInput.value.trim();
        if (!text) {
            alert('Please enter a review to analyze!');
            return;
        }

        analyzeBtn.disabled = true;
        const originalText = analyzeBtn.querySelector('.btn-text').textContent;
        analyzeBtn.querySelector('.btn-text').textContent = 'Analyzing...';

        try {
            const response = await fetch('/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text }),
            });

            const data = await response.json();

            if (data.error) {
                alert(data.error);
                return;
            }

            displayResults(data);
            totalReviews++;
            totalReviewsEl.textContent = totalReviews;
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred while analyzing the review.');
        } finally {
            analyzeBtn.disabled = false;
            analyzeBtn.querySelector('.btn-text').textContent = originalText;
        }
    });

    function displayResults(data) {
        // Show results, hide empty state
        emptyState.style.display = 'none';
        resultsContainer.classList.remove('results-hidden');

        // Update sentiment
        const sentiment = data.sentiment;
        sentimentText.textContent = sentiment;

        // Update sentiment icon and class
        const iconMap = {
            'Positive': '😊',
            'Negative': '😞',
            'Neutral': '😐'
        };

        const icon = sentimentBadge.querySelector('.sentiment-icon');
        icon.textContent = iconMap[sentiment] || '😊';

        // Update sentiment badge class
        sentimentBadge.className = 'sentiment-display ' + sentiment.toLowerCase();

        // Update aspects
        aspectsGrid.innerHTML = '';
        const aspectCounts = { Positive: 0, Negative: 0, Neutral: 0 };

        for (const [aspect, aspectSentiment] of Object.entries(data.aspects)) {
            if (aspectSentiment === 'Not Mentioned') continue;

            const div = document.createElement('div');
            div.className = 'aspect-tag ' + aspectSentiment.toLowerCase();

            if (aspectSentiment === 'Positive') {
                aspectCounts.Positive++;
            } else if (aspectSentiment === 'Negative') {
                aspectCounts.Negative++;
            } else {
                aspectCounts.Neutral++;
            }

            div.innerHTML = `
                <div class="aspect-tag-name">${aspect}</div>
                <div class="aspect-tag-sentiment">${aspectSentiment}</div>
            `;
            aspectsGrid.appendChild(div);
        }

        // Update chart
        updateChart(aspectCounts);

        // Scroll to results
        resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    function updateChart(counts) {
        const ctx = document.getElementById('aspectChart').getContext('2d');

        if (aspectChart) {
            aspectChart.destroy();
        }

        aspectChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Positive', 'Negative', 'Neutral'],
                datasets: [{
                    data: [counts.Positive, counts.Negative, counts.Neutral],
                    backgroundColor: [
                        'rgba(16, 185, 129, 0.8)',
                        'rgba(239, 68, 68, 0.8)',
                        'rgba(245, 158, 11, 0.8)'
                    ],
                    borderColor: [
                        '#10b981',
                        '#ef4444',
                        '#f59e0b'
                    ],
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 15,
                            font: {
                                size: 12,
                                family: 'Inter'
                            }
                        }
                    }
                }
            }
        });
    }
});
