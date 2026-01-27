export interface GithubRepo {
    id: number;
    name: string;
    description: string | null;
    html_url: string;
    stargazers_count: number;
    language: string | null;
    updated_at: string;
    topics: string[];
}

export interface GithubResponse {
    repos: GithubRepo[];
    error: string | null;
}

const USERNAME = 'smadonkuan';

const MOCK_REPOS: GithubRepo[] = [
    {
        id: 1,
        name: "Security-Tools-Demo",
        description: "A collection of python scripts for penetration testing and security analysis. (Mock Data from Rate Limit)",
        html_url: "https://github.com/smadonkuan",
        stargazers_count: 128,
        language: "Python",
        updated_at: new Date().toISOString(),
        topics: ["security", "python", "pentesting"]
    },
    {
        id: 2,
        name: "CTF-Writeups-Demo",
        description: "Detailed solutions and walkthroughs for various Capture The Flag competitions. (Mock Data from Rate Limit)",
        html_url: "https://github.com/smadonkuan",
        stargazers_count: 45,
        language: "Markdown",
        updated_at: new Date().toISOString(),
        topics: ["ctf", "writeups"]
    },
    {
        id: 3,
        name: "Automated-Scanner-Demo",
        description: "Automated vulnerability scanner built with Go. (Mock Data from Rate Limit)",
        html_url: "https://github.com/smadonkuan",
        stargazers_count: 89,
        language: "Go",
        updated_at: new Date().toISOString(),
        topics: ["security", "go", "scanner"]
    }
];

export async function getGithubRepos(): Promise<GithubResponse> {
    try {
        console.log(`Fetching GitHub repos for ${USERNAME}...`);
        const response = await fetch(`https://api.github.com/users/${USERNAME}/repos?sort=updated&per_page=100`);

        if (!response.ok) {
            console.error(`Failed to fetch GitHub repos: ${response.statusText}`);
            // Return empty array and error, NO mock data
            return {
                repos: [],
                error: `API ${response.status} ${response.statusText}`
            };
        }

        const repos: GithubRepo[] = await response.json();

        // Filter out the portfolio repo itself and forks if desired
        const filteredRepos = repos.filter(repo => repo.name !== 'smadonkuan.github.io');

        return { repos: filteredRepos, error: null };

    } catch (error) {
        console.error('Error fetching GitHub repos:', error);
        return {
            repos: [],
            error: 'Network/Fetch Error'
        };
    }
}
