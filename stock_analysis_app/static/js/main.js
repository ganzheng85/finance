// Stock Analysis Dashboard - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('analysisForm');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const resultsCard = document.getElementById('resultsCard');
    const resultsContent = document.getElementById('resultsContent');

    // Form submission
    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        // Get form data
        const ticker = document.getElementById('ticker').value.trim().toUpperCase();
        const reportTypes = [];

        document.querySelectorAll('input[name="report_type"]:checked').forEach(checkbox => {
            reportTypes.push(checkbox.value);
        });

        // Validation
        if (!ticker) {
            showError('Please enter a stock ticker symbol');
            return;
        }

        if (reportTypes.length === 0) {
            showError('Please select at least one report type');
            return;
        }

        // Show loading state
        setLoadingState(true);
        resultsCard.style.display = 'none';

        try {
            // Get current language (set by language selector)
            const language = window.currentLanguage || 'en';

            // Call API
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    ticker: ticker,
                    report_types: reportTypes,
                    language: language
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Analysis failed');
            }

            // Display results
            displayResults(data);

        } catch (error) {
            showError(error.message);
        } finally {
            setLoadingState(false);
        }
    });

    function setLoadingState(loading) {
        const btnText = analyzeBtn.querySelector('.btn-text');
        const btnLoading = analyzeBtn.querySelector('.btn-loading');

        if (loading) {
            btnText.style.display = 'none';
            btnLoading.style.display = 'flex';
            btnLoading.style.alignItems = 'center';
            btnLoading.style.justifyContent = 'center';
            analyzeBtn.disabled = true;
        } else {
            btnText.style.display = 'inline';
            btnLoading.style.display = 'none';
            analyzeBtn.disabled = false;
        }
    }

    function displayResults(data) {
        resultsContent.innerHTML = '';

        // Add header
        const header = document.createElement('div');
        header.style.marginBottom = '1.5rem';
        header.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem;">
                <h3 style="font-size: 1.25rem; font-weight: 600; color: var(--text-primary);">
                    ${data.ticker} Analysis
                </h3>
                <span style="color: var(--text-secondary); font-size: 0.9rem;">
                    ${new Date(data.timestamp).toLocaleString()}
                </span>
            </div>
        `;
        resultsContent.appendChild(header);

        // Add each report result
        data.reports.forEach(report => {
            const resultItem = createResultItem(report);
            resultsContent.appendChild(resultItem);
        });

        // Show results card with animation
        resultsCard.style.display = 'block';
        resultsCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    function createResultItem(report) {
        const div = document.createElement('div');
        div.className = `result-item ${report.status}`;

        const icon = getReportIcon(report.type);
        const title = getReportTitle(report.type);

        let content = `
            <div class="result-header">
                <div class="result-title">
                    <span>${icon}</span>
                    ${title}
                </div>
                <span class="status-badge ${report.status}">
                    ${report.status === 'success' ? '✓ Generated' : '✗ Failed'}
                </span>
            </div>
        `;

        if (report.status === 'success') {
            // Add note for fundamental reports
            if (report.type === 'fundamental' && report.note) {
                content += `
                    <div class="result-note" style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 12px; margin: 12px 0; font-size: 0.9em; color: #856404;">
                        ${report.note}
                    </div>
                `;
            }

            // Add instruction for comprehensive analysis
            if (report.type === 'fundamental' && report.instruction) {
                content += `
                    <div class="result-note" style="background: #e3f2fd; border-left: 4px solid #2196f3; padding: 12px; margin: 12px 0; font-size: 0.95em; color: #0d47a1;">
                        <strong>💡 For Comprehensive Analysis:</strong><br>
                        <code style="background: white; padding: 4px 8px; border-radius: 3px; display: inline-block; margin-top: 6px; color: #2196f3;">${report.instruction}</code>
                    </div>
                `;
            }

            content += `
                <div class="result-actions">
            `;

            // Add HTML view button if available
            if (report.html_url) {
                content += `
                    <a href="${report.html_url}" target="_blank" class="btn-secondary">
                        📄 View Report
                    </a>
                `;
            }

            content += `
                    <a href="${report.url}" download class="btn-secondary">
                        📥 Download Markdown
                    </a>
                </div>`;

            // Add chart preview for technical analysis
            if (report.type === 'technical' && report.chart_url) {
                content += `
                    <div class="chart-preview">
                        <img src="${report.chart_url}" alt="Technical Analysis Chart">
                    </div>
                `;
            }
        } else {
            content += `
                <div class="error-message">
                    Error: ${report.error}
                </div>
            `;
        }

        div.innerHTML = content;
        return div;
    }

    function getReportIcon(type) {
        const icons = {
            'fundamental': '📊',
            'technical': '📈'
            // 'action_plan': '🎯'  // Disabled for now
        };
        return icons[type] || '📄';
    }

    function getReportTitle(type) {
        const titles = {
            'fundamental': 'Fundamental Research Report',
            'technical': 'Technical Analysis Report'
            // 'action_plan': 'Potential Scenario Analysis'  // Disabled for now
        };
        return titles[type] || 'Report';
    }

    function showError(message) {
        const alert = document.createElement('div');
        alert.className = 'alert error';
        alert.innerHTML = `
            <span class="alert-icon">⚠️</span>
            <span>${message}</span>
        `;

        // Insert after form
        form.parentNode.insertBefore(alert, form.nextSibling);

        // Remove after 5 seconds
        setTimeout(() => {
            alert.remove();
        }, 5000);
    }

    // Auto-focus ticker input
    document.getElementById('ticker').focus();

    // Convert ticker to uppercase as user types
    document.getElementById('ticker').addEventListener('input', function(e) {
        this.value = this.value.toUpperCase();
    });
});
