export type GitHubLanguage = {
    language: string
    repo_count: number
}

export type GitHubLanguageStats = {
    languages: GitHubLanguage[]
}

export type GitRepos = {
    total_repositories: number
}

export type GitHubStatistics = {
    account_age_days: number
    account_age_years: number
    languages: GitHubLanguageStats
    repositories: GitRepos
}

export type GitHubData = {
    statistics: GitHubStatistics
}