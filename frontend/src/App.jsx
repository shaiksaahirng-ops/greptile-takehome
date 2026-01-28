import { useState, useEffect } from 'react'

// API URL - uses Vite proxy in dev, direct URL in production
const API_URL = import.meta.env.PROD ? '' : '';

export default function App() {
    const [changelogs, setChangelogs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchChangelogs();
    }, []);

    async function fetchChangelogs() {
        try {
            setLoading(true);
            setError(null);
            const response = await fetch(`${API_URL}/api/changelogs`);
            if (!response.ok) {
                throw new Error(`Failed to fetch changelogs: ${response.statusText}`);
            }
            const data = await response.json();
            setChangelogs(data);
        } catch (err) {
            console.error('Error fetching changelogs:', err);
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }

    return (
        <div className="app">
            <Header />
            <main className="container">
                <ChangelogList
                    changelogs={changelogs}
                    loading={loading}
                    error={error}
                />
            </main>
            <Footer />
        </div>
    );
}

function Header() {
    return (
        <header className="header">
            <div className="container">
                <div className="header__badge">
                    <span className="header__badge-dot"></span>
                    Latest Updates
                </div>
                <h1 className="header__title">What's New</h1>
                <p className="header__subtitle">
                    Stay up to date with the latest features, improvements, and fixes.
                </p>
            </div>
        </header>
    );
}

function ChangelogList({ changelogs, loading, error }) {
    if (loading) {
        return (
            <div className="changelog-list">
                <div className="loading">
                    <div className="loading__spinner"></div>
                    <span className="loading__text">Loading changelogs...</span>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="changelog-list">
                <div className="error">
                    <div className="error__icon">!</div>
                    <p className="error__message">Unable to load changelogs</p>
                    <p className="error__details">{error}</p>
                </div>
            </div>
        );
    }

    if (changelogs.length === 0) {
        return (
            <div className="changelog-list">
                <div className="changelog-list__empty">
                    <div className="changelog-list__empty-icon"></div>
                    <h3>No changelogs yet</h3>
                    <p>Use the CLI to generate and publish your first changelog!</p>
                </div>
            </div>
        );
    }

    return (
        <section className="changelog-list">
            <div className="changelog-list__items">
                {changelogs.map((changelog) => (
                    <ChangelogEntry key={changelog.id} changelog={changelog} />
                ))}
            </div>
        </section>
    );
}

function ChangelogEntry({ changelog }) {
    const formattedDate = new Date(changelog.created_at).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });

    const categories = [
        { key: 'features', label: 'New Features', icon: '+' },
        { key: 'improvements', label: 'Improvements', icon: '^' },
        { key: 'bugfixes', label: 'Bug Fixes', icon: 'x' },
        { key: 'breaking', label: 'Breaking Changes', icon: '!' },
    ];

    const hasChanges = categories.some(
        cat => changelog.changes[cat.key]?.length > 0
    );

    return (
        <article className="changelog-entry">
            <div className="changelog-entry__dot"></div>

            <div className="changelog-entry__header">
                <span className="changelog-entry__version">{changelog.version}</span>
                <time className="changelog-entry__date">{formattedDate}</time>
            </div>

            <h2 className="changelog-entry__title">{changelog.title}</h2>

            {changelog.summary && (
                <p className="changelog-entry__summary">{changelog.summary}</p>
            )}

            {hasChanges && (
                <div className="changelog-entry__changes">
                    {categories.map(({ key, label, icon }) => {
                        const items = changelog.changes[key];
                        if (!items || items.length === 0) return null;

                        return (
                            <div key={key} className={`change-category change-category--${key}`}>
                                <div className="change-category__header">
                                    <span className="change-category__icon">{icon}</span>
                                    {label}
                                </div>
                                <ul className="change-category__list">
                                    {items.map((item, index) => (
                                        <li key={index} className="change-category__item">
                                            {item}
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        );
                    })}
                </div>
            )}
        </article>
    );
}

function Footer() {
    return (
        <footer className="footer">
            <div className="container">
                <p className="footer__text">
                    Powered by{' '}
                    <a href="https://github.com" className="footer__link" target="_blank" rel="noopener noreferrer">
                        Changelog AI
                    </a>
                    {' '}• Generated with Gemini
                </p>
            </div>
        </footer>
    );
}
