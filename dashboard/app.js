// GitHub Traffic Analytics Dashboard
// Main application logic

class GitHubTrafficDashboard {
    constructor() {
        this.username = '';
        this.token = '';
        this.repositories = [];
        this.trafficData = {};
        this.charts = {};
    }

    async initialize(username, token) {
        this.username = username;
        this.token = token;

        if (!username || !token) {
            showError('Please enter both username and token');
            return;
        }

        try {
            showLoading();
            await this.fetchRepositories();
            await this.fetchTrafficData();
            this.renderDashboard();
            showSuccess('Dashboard loaded successfully!');
        } catch (error) {
            console.error('Error initializing dashboard:', error);
            showError(`Error: ${error.message}`);
        }
    }

    async fetchRepositories() {
        const headers = {
            'Authorization': `token ${this.token}`,
            'Accept': 'application/vnd.github.v3+json'
        };

        let page = 1;
        let allRepos = [];
        let hasMore = true;

        while (hasMore) {
            const response = await axios.get(
                `https://api.github.com/user/repos?page=${page}&per_page=100&sort=updated&direction=desc`,
                { headers }
            );

            allRepos = allRepos.concat(response.data);
            hasMore = response.data.length === 100;
            page++;
        }

        this.repositories = allRepos.filter(repo => !repo.fork);
        console.log(`Fetched ${this.repositories.length} repositories`);
    }

    async fetchTrafficData() {
        const headers = {
            'Authorization': `token ${this.token}`,
            'Accept': 'application/vnd.github.v3+json'
        };

        for (const repo of this.repositories) {
            try {
                // Fetch views
                const viewsResponse = await axios.get(
                    `https://api.github.com/repos/${this.username}/${repo.name}/traffic/views`,
                    { headers }
                );

                // Fetch clones
                const clonesResponse = await axios.get(
                    `https://api.github.com/repos/${this.username}/${repo.name}/traffic/clones`,
                    { headers }
                );

                this.trafficData[repo.name] = {
                    name: repo.name,
                    views: viewsResponse.data.views || [],
                    clones: clonesResponse.data.clones || [],
                    stars: repo.stargazers_count,
                    language: repo.language || 'N/A',
                    url: repo.html_url,
                    description: repo.description || ''
                };

                // Rate limiting: add small delay
                await new Promise(resolve => setTimeout(resolve, 100));
            } catch (error) {
                console.warn(`Could not fetch traffic for ${repo.name}:`, error.message);
                this.trafficData[repo.name] = {
                    name: repo.name,
                    views: [],
                    clones: [],
                    stars: repo.stargazers_count,
                    language: repo.language || 'N/A',
                    url: repo.html_url,
                    description: repo.description || ''
                };
            }
        }
    }

    renderDashboard() {
        this.updateStats();
        this.renderCharts();
        this.renderTable();
        document.getElementById('last-updated').textContent = new Date().toLocaleString();
    }

    updateStats() {
        let totalViews = 0;
        let totalClones = 0;
        let totalStars = 0;

        Object.values(this.trafficData).forEach(repo => {
            const views = repo.views.reduce((sum, d) => sum + d.count, 0);
            const clones = repo.clones.reduce((sum, d) => sum + d.count, 0);
            totalViews += views;
            totalClones += clones;
            totalStars += repo.stars;
        });

        document.getElementById('total-repos').textContent = this.repositories.length;
        document.getElementById('total-views').textContent = totalViews.toLocaleString();
        document.getElementById('total-clones').textContent = totalClones.toLocaleString();
        document.getElementById('total-stars').textContent = totalStars.toLocaleString();
    }

    renderCharts() {
        this.renderTrafficOverTimeChart();
        this.renderRepositoryComparisonChart();
        this.renderViewsVsClonesChart();
        this.renderTopRepositoriesChart();
    }

    renderTrafficOverTimeChart() {
        const ctx = document.getElementById('trafficChart').getContext('2d');
        
        // Aggregate data by date
        const dateMap = {};
        Object.values(this.trafficData).forEach(repo => {
            repo.views.forEach(view => {
                if (!dateMap[view.timestamp]) {
                    dateMap[view.timestamp] = { views: 0, clones: 0 };
                }
                dateMap[view.timestamp].views += view.count;
            });
            repo.clones.forEach(clone => {
                if (!dateMap[clone.timestamp]) {
                    dateMap[clone.timestamp] = { views: 0, clones: 0 };
                }
                dateMap[clone.timestamp].clones += clone.count;
            });
        });

        const dates = Object.keys(dateMap).sort();
        const views = dates.map(d => dateMap[d].views);
        const clones = dates.map(d => dateMap[d].clones);

        this.charts.traffic = new Chart(ctx, {
            type: 'line',
            data: {
                labels: dates.map(d => new Date(d).toLocaleDateString()),
                datasets: [
                    {
                        label: 'Views',
                        data: views,
                        borderColor: '#0366d6',
                        backgroundColor: 'rgba(3, 102, 214, 0.1)',
                        borderWidth: 2,
                        tension: 0.4,
                        fill: true
                    },
                    {
                        label: 'Clones',
                        data: clones,
                        borderColor: '#6f42c1',
                        backgroundColor: 'rgba(111, 66, 193, 0.1)',
                        borderWidth: 2,
                        tension: 0.4,
                        fill: true
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { display: true }
                },
                scales: {
                    y: { beginAtZero: true }
                }
            }
        });
    }

    renderRepositoryComparisonChart() {
        const ctx = document.getElementById('reposChart').getContext('2d');
        
        const repoNames = Object.keys(this.trafficData).slice(0, 10);
        const viewsData = repoNames.map(name => {
            return this.trafficData[name].views.reduce((sum, d) => sum + d.count, 0);
        });
        const clonesData = repoNames.map(name => {
            return this.trafficData[name].clones.reduce((sum, d) => sum + d.count, 0);
        });

        this.charts.repos = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: repoNames,
                datasets: [
                    {
                        label: 'Views',
                        data: viewsData,
                        backgroundColor: '#0366d6',
                        borderRadius: 4
                    },
                    {
                        label: 'Clones',
                        data: clonesData,
                        backgroundColor: '#6f42c1',
                        borderRadius: 4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { display: true }
                },
                scales: {
                    y: { beginAtZero: true }
                }
            }
        });
    }

    renderViewsVsClonesChart() {
        const ctx = document.getElementById('viewsVsClonesChart').getContext('2d');
        
        let totalViews = 0;
        let totalClones = 0;

        Object.values(this.trafficData).forEach(repo => {
            totalViews += repo.views.reduce((sum, d) => sum + d.count, 0);
            totalClones += repo.clones.reduce((sum, d) => sum + d.count, 0);
        });

        this.charts.viewsVsClones = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Views', 'Clones'],
                datasets: [{
                    data: [totalViews, totalClones],
                    backgroundColor: ['#0366d6', '#6f42c1'],
                    borderColor: white,
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { position: 'bottom' }
                }
            }
        });
    }

    renderTopRepositoriesChart() {
        const ctx = document.getElementById('topReposChart').getContext('2d');
        
        const sortedRepos = Object.values(this.trafficData)
            .sort((a, b) => {
                const aViews = a.views.reduce((sum, d) => sum + d.count, 0);
                const bViews = b.views.reduce((sum, d) => sum + d.count, 0);
                return bViews - aViews;
            })
            .slice(0, 8);

        this.charts.topRepos = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: sortedRepos.map(r => r.name),
                datasets: [{
                    label: 'Total Views',
                    data: sortedRepos.map(r => r.views.reduce((sum, d) => sum + d.count, 0)),
                    backgroundColor: '#28a745',
                    borderRadius: 4
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: true,
                scales: {
                    x: { beginAtZero: true }
                }
            }
        });
    }

    renderTable() {
        const tbody = document.querySelector('#repoTable tbody');
        tbody.innerHTML = '';

        Object.values(this.trafficData).forEach(repo => {
            const views = repo.views.reduce((sum, d) => sum + d.count, 0);
            const clones = repo.clones.reduce((sum, d) => sum + d.count, 0);

            const row = document.createElement('tr');
            row.innerHTML = `
                <td><strong>${repo.name}</strong><br><small>${repo.description}</small></td>
                <td>${views.toLocaleString()}</td>
                <td>${clones.toLocaleString()}</td>
                <td>${repo.stars.toLocaleString()}</td>
                <td>${repo.language}</td>
                <td>
                    <a href="${repo.url}" target="_blank">GitHub</a>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    exportToCSV() {
        let csv = 'Repository,Views,Clones,Stars,Language\n';
        
        Object.values(this.trafficData).forEach(repo => {
            const views = repo.views.reduce((sum, d) => sum + d.count, 0);
            const clones = repo.clones.reduce((sum, d) => sum + d.count, 0);
            csv += `"${repo.name}",${views},${clones},${repo.stars},"${repo.language}"\n`;
        });

        const blob = new Blob([csv], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `github-traffic-${new Date().getTime()}.csv`;
        a.click();
    }

    exportToJSON() {
        const data = {
            username: this.username,
            exportedAt: new Date().toISOString(),
            repositories: Object.values(this.trafficData).map(repo => ({
                name: repo.name,
                views: repo.views.reduce((sum, d) => sum + d.count, 0),
                clones: repo.clones.reduce((sum, d) => sum + d.count, 0),
                stars: repo.stars,
                language: repo.language,
                url: repo.url
            }))
        };

        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `github-traffic-${new Date().getTime()}.json`;
        a.click();
    }
}

// Global instance
const dashboard = new GitHubTrafficDashboard();

// UI Helper Functions
function initializeDashboard() {
    const username = document.getElementById('username').value;
    const token = document.getElementById('token').value;
    dashboard.initialize(username, token);
}

function refreshData() {
    const username = document.getElementById('username').value;
    const token = document.getElementById('token').value;
    dashboard.initialize(username, token);
}

function exportToCSV() {
    dashboard.exportToCSV();
}

function exportToJSON() {
    dashboard.exportToJSON();
}

function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error';
    errorDiv.textContent = message;
    const container = document.querySelector('.setup-section');
    container.insertBefore(errorDiv, container.firstChild);
    setTimeout(() => errorDiv.remove(), 5000);
}

function showSuccess(message) {
    const successDiv = document.createElement('div');
    successDiv.className = 'success';
    successDiv.textContent = message;
    const container = document.querySelector('.setup-section');
    container.insertBefore(successDiv, container.firstChild);
    setTimeout(() => successDiv.remove(), 5000);
}

function showLoading() {
    console.log('Loading data...');
}

// Load credentials from localStorage if available
window.addEventListener('load', () => {
    const savedUsername = localStorage.getItem('github_username');
    if (savedUsername) {
        document.getElementById('username').value = savedUsername;
    }
});

// Save credentials to localStorage
document.getElementById('username')?.addEventListener('change', (e) => {
    localStorage.setItem('github_username', e.target.value);
});