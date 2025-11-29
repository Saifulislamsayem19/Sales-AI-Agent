// Sales Analytics AI Agent - Frontend Application

const API_BASE = window.location.origin;

class SalesAnalyticsApp {
    constructor() {
        this.currentView = 'chat';
        this.init();
    }

    async init() {
        this.setupEventListeners();
        await this.loadQuickStats();
        await this.checkHealth();
    }

    setupEventListeners() {
        // Navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => this.switchView(e.target.closest('.nav-item').dataset.view));
        });

        // Chat input
        const chatInput = document.getElementById('chat-input');
        const sendButton = document.getElementById('send-button');

        sendButton.addEventListener('click', () => this.sendMessage());
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Example queries
        document.querySelectorAll('.example-query').forEach(btn => {
            btn.addEventListener('click', (e) => {
                chatInput.value = e.target.textContent.replace(/"/g, '');
                this.sendMessage();
            });
        });
    }

    async switchView(view) {
        this.currentView = view;

        // Update navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.toggle('active', item.dataset.view === view);
        });

        // Update content
        document.querySelectorAll('.view-container').forEach(container => {
            container.classList.add('hidden');
        });
        document.getElementById(`${view}-view`).classList.remove('hidden');

        // Update header
        const titles = {
            chat: { title: 'AI Assistant', subtitle: 'Ask anything about your sales data' },
            dashboard: { title: 'Dashboard', subtitle: 'Visual analytics overview' },
            descriptive: { title: 'Descriptive Analytics', subtitle: 'What has happened?' },
            diagnostic: { title: 'Diagnostic Analytics', subtitle: 'Why did it happen?' },
            predictive: { title: 'Predictive Analytics', subtitle: 'What is likely to happen?' },
            prescriptive: { title: 'Prescriptive Analytics', subtitle: 'What actions should be taken?' }
        };

        document.getElementById('page-title').textContent = titles[view].title;
        document.getElementById('page-subtitle').textContent = titles[view].subtitle;

        // Load view data
        switch(view) {
            case 'dashboard':
                await this.loadDashboard();
                break;
            case 'descriptive':
                await this.loadDescriptiveAnalytics();
                break;
            case 'diagnostic':
                await this.loadDiagnosticAnalytics();
                break;
            case 'predictive':
                await this.loadPredictiveAnalytics();
                break;
            case 'prescriptive':
                await this.loadPrescriptiveAnalytics();
                break;
        }
    }

    async checkHealth() {
        try {
            const response = await fetch(`${API_BASE}/health`);
            const health = await response.json();
            
            const statusDot = document.querySelector('.status-dot');
            const statusText = document.querySelector('.status-text');
            
            if (health.status === 'healthy') {
                statusDot.style.background = '#10b981';
                statusText.textContent = 'System Active';
            }
        } catch (error) {
            console.error('Health check failed:', error);
        }
    }

    async loadQuickStats() {
        try {
            const response = await fetch(`${API_BASE}/api/summary`);
            const data = await response.json();

            document.getElementById('stat-sales').textContent = this.formatCurrency(data.total_sales);
            document.getElementById('stat-orders').textContent = this.formatNumber(data.total_orders);
            document.getElementById('stat-margin').textContent = `${data.profit_margin.toFixed(1)}%`;
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    }

    async sendMessage() {
        const input = document.getElementById('chat-input');
        const message = input.value.trim();

        if (!message) return;

        const sendButton = document.getElementById('send-button');
        sendButton.disabled = true;
        sendButton.textContent = 'Thinking...';

        // Add user message
        this.addMessage(message, 'user');
        input.value = '';

        try {
            const response = await fetch(`${API_BASE}/api/query`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: message })
            });

            const data = await response.json();
            this.addMessage(data.answer, 'agent', data);

        } catch (error) {
            console.error('Error:', error);
            this.addMessage('Sorry, I encountered an error. Please try again.', 'agent');
        } finally {
            sendButton.disabled = false;
            sendButton.textContent = 'Send';
        }
    }

    addMessage(content, type, metadata = null) {
        const messagesContainer = document.getElementById('chat-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;

        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.textContent = type === 'user' ? '👤' : '🤖';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';

        let html = `<div class="message-text">${this.formatMessageContent(content)}</div>`;

        if (metadata) {
            html += `<div class="message-meta">`;
            html += `<span>📊 ${metadata.analytics_type}</span>`;
            html += `<span>⏱️ ${metadata.execution_time}s</span>`;
            if (metadata.confidence) {
                html += `<span>📈 ${(metadata.confidence * 100).toFixed(0)}% confidence</span>`;
            }
            html += `</div>`;

            if (metadata.insights && metadata.insights.length > 0) {
                html += `<div class="insights">`;
                html += `<h4>Key Insights</h4><ul>`;
                metadata.insights.forEach(insight => {
                    html += `<li>${insight}</li>`;
                });
                html += `</ul></div>`;
            }

            if (metadata.recommendations && metadata.recommendations.length > 0) {
                html += `<div class="recommendations">`;
                html += `<h4>Recommendations</h4><ul>`;
                metadata.recommendations.forEach(rec => {
                    html += `<li>${rec}</li>`;
                });
                html += `</ul></div>`;
            }
        }

        contentDiv.innerHTML = html;
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(contentDiv);
        messagesContainer.appendChild(messageDiv);

        // Scroll to bottom
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    formatMessageContent(content) {
        let html = content;
        
        // Protect code blocks
        const codeBlocks = [];
        html = html.replace(/```([\s\S]*?)```/g, (match, code) => {
            codeBlocks.push(code);
            return `___CODE_BLOCK_${codeBlocks.length - 1}___`;
        });
        
        // Protect inline code
        const inlineCodes = [];
        html = html.replace(/`([^`]+)`/g, (match, code) => {
            inlineCodes.push(code);
            return `___INLINE_CODE_${inlineCodes.length - 1}___`;
        });
        
        // Process headers (must come before other formatting)
        html = html.replace(/^#### (.+)$/gm, '<h4 class="md-h5">$1</h4>');
        html = html.replace(/^### (.+)$/gm, '<h4 class="md-h4">$1</h4>');
        html = html.replace(/^## (.+)$/gm, '<h3 class="md-h3">$1</h3>');
        html = html.replace(/^# (.+)$/gm, '<h2 class="md-h2">$1</h2>');
        
        // Bold text
        html = html.replace(/\*\*([^\*]+)\*\*/g, '<strong>$1</strong>');
        html = html.replace(/__([^_]+)__/g, '<strong>$1</strong>');
        
        // Process tables
        const tableRegex = /(\|[^\n]+\|\n)+/g;
        html = html.replace(tableRegex, (match) => {
            const rows = match.trim().split('\n');
            let tableHtml = '<table class="md-table">';
            
            rows.forEach((row, index) => {
                if (row.includes('---')) return; // Skip separator row
                
                const cells = row.split('|').filter(cell => cell.trim());
                const tag = index === 0 ? 'th' : 'td';
                tableHtml += '<tr>';
                cells.forEach(cell => {
                    tableHtml += `<${tag}>${cell.trim()}</${tag}>`;
                });
                tableHtml += '</tr>';
            });
            
            tableHtml += '</table>';
            return tableHtml;
        });
        
        // Process unordered lists
        html = html.replace(/^[\*\-\•] (.+)$/gm, '<li>$1</li>');
        html = html.replace(/(<li>.*?<\/li>\n?)+/g, '<ul class="md-list">$&</ul>');
        
        // Process numbered lists
        html = html.replace(/^\d+\.\s+(.+)$/gm, '<li>$1</li>');
        
        // Restore code blocks
        codeBlocks.forEach((code, index) => {
            html = html.replace(`___CODE_BLOCK_${index}___`, 
                `<pre class="md-pre"><code>${this.escapeHtml(code)}</code></pre>`);
        });
        
        // Restore inline code
        inlineCodes.forEach((code, index) => {
            html = html.replace(`___INLINE_CODE_${index}___`, 
                `<code class="md-code">${this.escapeHtml(code)}</code>`);
        });
        
        // Convert double line breaks to paragraph breaks
        html = html.split(/\n\n+/).map(para => {
            // Don't wrap if it's already a block element
            if (para.match(/^<(h[1-6]|ul|ol|table|pre|div)/)) {
                return para;
            }
            return `<p class="md-p">${para.replace(/\n/g, '<br>')}</p>`;
        }).join('\n');
        
        return `<div class="markdown-content">${html}</div>`;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    async loadDashboard() {
        try {
            const response = await fetch(`${API_BASE}/api/analytics/descriptive`);
            const data = await response.json();

            // Time series chart
            this.createTimeSeriesChart(data.time_series_analysis);

            // Category chart
            this.createCategoryChart(data.category_analysis);

            // Regional chart
            this.createRegionalChart(data.regional_analysis);

            // Sales overview
            this.createSalesOverviewChart(data.summary_statistics);

        } catch (error) {
            console.error('Error loading dashboard:', error);
        }
    }

    async loadDescriptiveAnalytics() {
        const container = document.getElementById('descriptive-content');
        container.innerHTML = '<div class="loading-spinner">Loading...</div>';

        try {
            const response = await fetch(`${API_BASE}/api/analytics/descriptive`);
            const data = await response.json();

            let html = '';

            // Summary Statistics
            html += `<div class="section">`;
            html += `<h3>📊 Summary Statistics</h3>`;
            html += `<div class="metrics-grid">`;
            const overview = data.summary_statistics.overview;
            html += `<div class="metric-box"><div class="label">Total Sales</div><div class="value">${this.formatCurrency(overview.total_sales)}</div></div>`;
            html += `<div class="metric-box"><div class="label">Total Profit</div><div class="value">${this.formatCurrency(overview.total_profit)}</div></div>`;
            html += `<div class="metric-box"><div class="label">Orders</div><div class="value">${this.formatNumber(overview.total_orders)}</div></div>`;
            html += `<div class="metric-box"><div class="label">Customers</div><div class="value">${this.formatNumber(overview.total_customers)}</div></div>`;
            html += `<div class="metric-box"><div class="label">Avg Order Value</div><div class="value">${this.formatCurrency(overview.avg_order_value)}</div></div>`;
            html += `<div class="metric-box"><div class="label">Profit Margin</div><div class="value">${overview.profit_margin.toFixed(1)}%</div></div>`;
            html += `</div></div>`;

            // Category Analysis
            html += `<div class="section"><h3>📦 Category Analysis</h3>`;
            html += `<div id="desc-category-chart"></div></div>`;

            // Regional Analysis
            html += `<div class="section"><h3>🌍 Regional Analysis</h3>`;
            html += `<div id="desc-regional-chart"></div></div>`;

            container.innerHTML = html;

            // Render charts
            if (data.category_analysis.categories) {
                this.createBarChart('desc-category-chart', 
                    data.category_analysis.categories.map(c => c.Category),
                    data.category_analysis.categories.map(c => c.Sales_sum),
                    'Sales by Category'
                );
            }

            if (data.regional_analysis.regions) {
                this.createBarChart('desc-regional-chart',
                    data.regional_analysis.regions.map(r => r.Region),
                    data.regional_analysis.regions.map(r => r.Total_Sales),
                    'Sales by Region'
                );
            }

        } catch (error) {
            container.innerHTML = `<div class="section">Error loading analytics: ${error.message}</div>`;
        }
    }

    async loadDiagnosticAnalytics() {
        const container = document.getElementById('diagnostic-content');
        container.innerHTML = '<div class="loading-spinner">Loading...</div>';

        try {
            const response = await fetch(`${API_BASE}/api/analytics/diagnostic`);
            const data = await response.json();

            let html = '';

            // Anomalies
            if (data.anomalies) {
                html += `<div class="section">`;
                html += `<h3>🔍 Anomaly Detection</h3>`;
                html += `<div class="metrics-grid">`;
                html += `<div class="metric-box"><div class="label">Anomalies Found</div><div class="value">${data.anomalies.total_anomalies}</div></div>`;
                html += `<div class="metric-box"><div class="label">Anomaly %</div><div class="value">${data.anomalies.anomaly_percentage.toFixed(2)}%</div></div>`;
                html += `</div></div>`;
            }

            // Correlations
            if (data.correlations && data.correlations.strong_correlations) {
                html += `<div class="section">`;
                html += `<h3>🔗 Strong Correlations</h3>`;
                html += `<ul>`;
                data.correlations.strong_correlations.slice(0, 5).forEach(corr => {
                    html += `<li><strong>${corr.metric1}</strong> and <strong>${corr.metric2}</strong>: ${(corr.correlation * 100).toFixed(1)}% (${corr.strength})</li>`;
                });
                html += `</ul></div>`;
            }

            // Discount Impact
            if (data.discount_impact) {
                html += `<div class="section">`;
                html += `<h3>💰 Discount Impact Analysis</h3>`;
                html += `<div id="discount-chart"></div>`;
                html += `<p style="margin-top: 1rem;"><strong>Recommendation:</strong> ${data.discount_impact.recommendation}</p>`;
                html += `</div>`;
            }

            container.innerHTML = html;

            // Render discount chart
            if (data.discount_impact && data.discount_impact.discount_impact) {
                this.createBarChart('discount-chart',
                    data.discount_impact.discount_impact.map(d => d.Discount_Bin),
                    data.discount_impact.discount_impact.map(d => d.Profit_Margin),
                    'Profit Margin by Discount Level'
                );
            }

        } catch (error) {
            container.innerHTML = `<div class="section">Error loading analytics: ${error.message}</div>`;
        }
    }

    async loadPredictiveAnalytics() {
        const container = document.getElementById('predictive-content');
        container.innerHTML = '<div class="loading-spinner">Loading...</div>';

        try {
            const response = await fetch(`${API_BASE}/api/analytics/predictive`);
            const data = await response.json();

            let html = '';

            // Sales Forecast
            if (data.sales_forecast) {
                html += `<div class="section">`;
                html += `<h3>📈 Sales Forecast</h3>`;
                html += `<div id="forecast-chart"></div>`;
                html += `<p style="margin-top: 1rem;">Trend: <strong>${data.sales_forecast.trend}</strong></p>`;
                html += `</div>`;
            }

            // Churn Prediction
            if (data.churn_prediction) {
                html += `<div class="section">`;
                html += `<h3>👥 Customer Churn Analysis</h3>`;
                html += `<div class="metrics-grid">`;
                html += `<div class="metric-box"><div class="label">Churn Rate</div><div class="value">${data.churn_prediction.churn_rate.toFixed(1)}%</div></div>`;
                Object.entries(data.churn_prediction.churn_summary).forEach(([risk, count]) => {
                    html += `<div class="metric-box"><div class="label">${risk} Risk</div><div class="value">${count}</div></div>`;
                });
                html += `</div></div>`;
            }

            // Growth Opportunities
            if (data.growth_opportunities && data.growth_opportunities.opportunities) {
                html += `<div class="section">`;
                html += `<h3>🚀 Growth Opportunities</h3>`;
                html += `<ul>`;
                data.growth_opportunities.opportunities.forEach(opp => {
                    html += `<li><strong>${opp.type}: ${opp.name}</strong> - ${opp.recommendation || opp.potential}</li>`;
                });
                html += `</ul></div>`;
            }

            container.innerHTML = html;

            // Render forecast chart
            if (data.sales_forecast && data.sales_forecast.forecasts) {
                this.createForecastChart('forecast-chart', data.sales_forecast.forecasts);
            }

        } catch (error) {
            container.innerHTML = `<div class="section">Error loading analytics: ${error.message}</div>`;
        }
    }

    async loadPrescriptiveAnalytics() {
        const container = document.getElementById('prescriptive-content');
        container.innerHTML = '<div class="loading-spinner">Loading...</div>';

        try {
            const response = await fetch(`${API_BASE}/api/analytics/prescriptive`);
            const data = await response.json();

            let html = '';

            // Action Plan
            if (data.action_plan) {
                html += `<div class="section">`;
                html += `<h3>📋 Strategic Action Plan</h3>`;
                
                html += `<h4 style="margin-top: 1.5rem;">Immediate Actions (Next 30 days)</h4>`;
                html += `<ul>`;
                data.action_plan.immediate_actions.forEach(action => {
                    html += `<li>${action}</li>`;
                });
                html += `</ul>`;

                html += `<h4 style="margin-top: 1.5rem;">Short-term Actions (30-90 days)</h4>`;
                html += `<ul>`;
                data.action_plan.short_term_actions.forEach(action => {
                    html += `<li>${action}</li>`;
                });
                html += `</ul>`;

                html += `<h4 style="margin-top: 1.5rem;">Long-term Actions (90+ days)</h4>`;
                html += `<ul>`;
                data.action_plan.long_term_actions.forEach(action => {
                    html += `<li>${action}</li>`;
                });
                html += `</ul>`;

                html += `</div>`;
            }

            // Pricing Optimization
            if (data.pricing_optimization && data.pricing_optimization.pricing_recommendations) {
                html += `<div class="section">`;
                html += `<h3>💲 Pricing Optimization</h3>`;
                html += `<ul>`;
                data.pricing_optimization.pricing_recommendations.forEach(rec => {
                    html += `<li><strong>${rec.category}:</strong> ${rec.action}`;
                    if (rec.expected_impact) html += ` (Expected impact: ${rec.expected_impact})`;
                    html += `</li>`;
                });
                html += `</ul></div>`;
            }

            // Marketing Optimization
            if (data.marketing_optimization && data.marketing_optimization.marketing_recommendations) {
                html += `<div class="section">`;
                html += `<h3>📢 Marketing Budget Optimization</h3>`;
                html += `<div id="marketing-chart"></div>`;
                html += `</div>`;
            }

            // Retention Strategy
            if (data.retention_strategy && data.retention_strategy.retention_strategies) {
                html += `<div class="section">`;
                html += `<h3>🎯 Customer Retention Strategies</h3>`;
                Object.entries(data.retention_strategy.retention_strategies).forEach(([segment, strategy]) => {
                    html += `<h4 style="margin-top: 1rem;">${segment}</h4>`;
                    html += `<p><strong>Strategy:</strong> ${strategy.strategy}</p>`;
                    html += `<ul>`;
                    strategy.actions.forEach(action => {
                        html += `<li>${action}</li>`;
                    });
                    html += `</ul>`;
                });
                html += `</div>`;
            }

            container.innerHTML = html;

            // Render marketing chart
            if (data.marketing_optimization && data.marketing_optimization.marketing_recommendations) {
                const recs = data.marketing_optimization.marketing_recommendations;
                this.createBarChart('marketing-chart',
                    recs.map(r => r.region),
                    recs.map(r => parseFloat(r.recommended_budget_allocation)),
                    'Recommended Budget Allocation (%)'
                );
            }

        } catch (error) {
            container.innerHTML = `<div class="section">Error loading analytics: ${error.message}</div>`;
        }
    }

    // Chart creation helpers
    createTimeSeriesChart(data) {
        if (!data || !data.time_series) return;

        const trace = {
            x: data.time_series.map(d => d.Order_Date),
            y: data.time_series.map(d => d.sum),
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Sales',
            line: { color: '#6366f1', width: 3 }
        };

        const layout = {
            title: '',
            paper_bgcolor: '#1e293b',
            plot_bgcolor: '#334155',
            font: { color: '#f1f5f9' },
            xaxis: { gridcolor: '#475569' },
            yaxis: { gridcolor: '#475569', title: 'Sales ($)' }
        };

        Plotly.newPlot('timeseries-chart', [trace], layout, { responsive: true });
    }

    createCategoryChart(data) {
        if (!data || !data.categories) return;

        const trace = {
            x: data.categories.map(c => c.Category),
            y: data.categories.map(c => c.Sales_sum),
            type: 'bar',
            marker: { color: '#6366f1' }
        };

        const layout = {
            paper_bgcolor: '#1e293b',
            plot_bgcolor: '#334155',
            font: { color: '#f1f5f9' },
            xaxis: { gridcolor: '#475569' },
            yaxis: { gridcolor: '#475569', title: 'Sales ($)' }
        };

        Plotly.newPlot('category-chart', [trace], layout, { responsive: true });
    }

    createRegionalChart(data) {
        if (!data || !data.regions) return;

        const trace = {
            labels: data.regions.map(r => r.Region),
            values: data.regions.map(r => r.Total_Sales),
            type: 'pie',
            marker: { colors: ['#6366f1', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981'] }
        };

        const layout = {
            paper_bgcolor: '#1e293b',
            font: { color: '#f1f5f9' }
        };

        Plotly.newPlot('regional-chart', [trace], layout, { responsive: true });
    }

    createSalesOverviewChart(data) {
        if (!data || !data.overview) return;

        const overview = data.overview;
        const trace = {
            x: ['Sales', 'Profit', 'Orders (×100)'],
            y: [overview.total_sales, overview.total_profit, overview.total_orders * 100],
            type: 'bar',
            marker: { color: ['#6366f1', '#10b981', '#f59e0b'] }
        };

        const layout = {
            paper_bgcolor: '#1e293b',
            plot_bgcolor: '#334155',
            font: { color: '#f1f5f9' },
            xaxis: { gridcolor: '#475569' },
            yaxis: { gridcolor: '#475569' }
        };

        Plotly.newPlot('sales-overview-chart', [trace], layout, { responsive: true });
    }

    createBarChart(elementId, categories, values, title) {
        const trace = {
            x: categories,
            y: values,
            type: 'bar',
            marker: { color: '#6366f1' }
        };

        const layout = {
            title: title,
            paper_bgcolor: '#1e293b',
            plot_bgcolor: '#334155',
            font: { color: '#f1f5f9' },
            xaxis: { gridcolor: '#475569' },
            yaxis: { gridcolor: '#475569' }
        };

        Plotly.newPlot(elementId, [trace], layout, { responsive: true });
    }

    createForecastChart(elementId, forecasts) {
        const trace = {
            x: forecasts.map(f => f.date),
            y: forecasts.map(f => f.forecast),
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Forecast',
            line: { color: '#6366f1', width: 3 }
        };

        const upperBound = {
            x: forecasts.map(f => f.date),
            y: forecasts.map(f => f.upper_bound),
            type: 'scatter',
            mode: 'lines',
            name: 'Upper Bound',
            line: { color: '#6366f1', width: 1, dash: 'dash' }
        };

        const lowerBound = {
            x: forecasts.map(f => f.date),
            y: forecasts.map(f => f.lower_bound),
            type: 'scatter',
            mode: 'lines',
            name: 'Lower Bound',
            line: { color: '#6366f1', width: 1, dash: 'dash' }
        };

        const layout = {
            title: 'Sales Forecast',
            paper_bgcolor: '#1e293b',
            plot_bgcolor: '#334155',
            font: { color: '#f1f5f9' },
            xaxis: { gridcolor: '#475569' },
            yaxis: { gridcolor: '#475569', title: 'Sales ($)' }
        };

        Plotly.newPlot(elementId, [lowerBound, trace, upperBound], layout, { responsive: true });
    }

    formatCurrency(value) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(value);
    }

    formatNumber(value) {
        return new Intl.NumberFormat('en-US').format(value);
    }
}

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    new SalesAnalyticsApp();
});
