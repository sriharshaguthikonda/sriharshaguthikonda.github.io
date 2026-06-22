# GitHub Traffic Analytics Dashboard

🚀 A feature-rich, intuitive dashboard to track and analyze traffic across all your GitHub repositories in one place.

## Features

✨ **Beautiful UI with Charts & Graphs**
- Real-time traffic visualization
- Views vs Clones comparison
- Repository performance charts
- Top repositories by views
- Traffic trends over time

📊 **Comprehensive Analytics**
- Total views and clones across all repos
- Per-repository detailed statistics
- Stars tracking
- Language detection
- 14-day historical data

💾 **Export & Share**
- Export data to CSV
- Export data to JSON
- Share analytics with team

🔐 **Secure & Private**
- No data stored on servers
- Runs entirely on your browser
- Your credentials are only used locally
- GitHub Personal Access Token only needs read access

## Setup

### Prerequisites
- GitHub account
- GitHub Personal Access Token with `public_repo` and `repo` scopes

### Getting Your Token

1. Go to [GitHub Settings → Developer settings → Personal access tokens](https://github.com/settings/tokens)
2. Click "Generate new token"
3. Select scopes:
   - ✓ `public_repo`
   - ✓ `repo`
4. Copy the token and keep it safe

### How to Use

1. **Visit the Dashboard**
   - Open `https://sriharshaguthikonda.github.io/dashboard/`

2. **Enter Your Credentials**
   - GitHub Username
   - GitHub Personal Access Token (optional but recommended for private repos)

3. **Click "Load Dashboard"**
   - Wait for data to load (this may take a minute if you have many repos)
   - All charts and stats will populate automatically

4. **Explore Your Analytics**
   - View traffic trends
   - Compare repository performance
   - Export data for further analysis

## Dashboard Sections

### 📈 Key Statistics
- Total repositories tracked
- Total views (14 days)
- Total clones (14 days)
- Total stars

### 📊 Charts
1. **Traffic Over Time**: Line chart showing daily views and clones
2. **Repository Comparison**: Bar chart comparing top 10 repos
3. **Views vs Clones**: Doughnut chart showing ratio
4. **Top Repositories**: Horizontal bar chart of most viewed repos

### 📋 Detailed Table
- Repository name and description
- Views and clones count
- Stars
- Programming language
- Direct links to GitHub

## Limitations

- GitHub API limits traffic data to **14 days** (this is GitHub's limitation)
- Rate limiting: 60 requests/hour for unauthenticated, 5000/hour for authenticated users
- Traffic data requires push access to read (GitHub API requirement)

## Troubleshooting

### "No data available"
- Ensure your repos have traffic (at least some views/clones)
- Check that your token is valid and has correct scopes
- Some repos may not have traffic data yet

### "401 Unauthorized"
- Your token might be invalid or expired
- Generate a new token and try again

### "404 Not Found"
- Make sure your username is correct
- Check token permissions

### Slow loading
- Dashboard loads data for each repository sequentially
- Having many repositories will take longer
- This is normal and expected

## Privacy & Security

✅ **Your data is safe:**
- Nothing is sent to external servers
- Dashboard runs 100% locally in your browser
- Credentials are only used for GitHub API calls
- Optional: Use browser's localStorage to remember username (token not saved)

## Technologies Used

- **Chart.js**: Beautiful interactive charts
- **Axios**: HTTP client for API requests
- **Vanilla JavaScript**: No heavy dependencies
- **GitHub REST API v3**: Real traffic data

## Contributing

Found a bug or have a feature request? Create an issue on [GitHub](https://github.com/sriharshaguthikonda/sriharshaguthikonda.github.io)

## License

MIT - Feel free to use this dashboard for your own purposes

## Support

For issues or questions:
1. Check the [troubleshooting section](#troubleshooting)
2. Review your GitHub token permissions
3. Check browser console for error messages
4. Create an issue on GitHub

---

**Happy Analytics! 🎉**