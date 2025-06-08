import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { GetCBZFile, GetChapters } from '../REST';

const MAX_DOWNLOADS = 5;

function Chapters() {
    const { title } = useParams();
    const [data, setData] = useState({});
    const [loading, setLoading] = useState(true);
    const [downloadingChapters, setDownloadingChapters] = useState(new Set());

    useEffect(() => {
        setLoading(true);
        GetChapters(title)
            .then((response) => {
                setData(JSON.parse(response));
                setLoading(false);
            })
            .catch((ex) => {
                console.log(ex);
                setData({});
                setLoading(false);
            });
    }, [title]);

    const handleChapterClick = (chapterTitle, url) => {
        setDownloadingChapters((currentSet) => {
            if (currentSet.size >= MAX_DOWNLOADS) {
                alert("Too many downloads in progress. Please wait.");
                return currentSet;
            }
    
            const newSet = new Set(currentSet);
            newSet.add(chapterTitle);
            downloadChapter(chapterTitle, url);
            return newSet;
        });
    };

    const options = { year: "numeric", month: "short", day: "2-digit" };
    
    const processDate = (data) => {
        if (data && data.length > 0) {
            const date = new Date(data);
            return date.toLocaleDateString("en-US", options);
        }
        return data;
    }

    const downloadChapter = (chapterTitle, url) => {
        GetCBZFile({ url, title, chapter: chapterTitle })
            .then((response) => {
                const url = window.URL.createObjectURL(new Blob([response], {
                    type: 'application/zip'  // CBZ = ZIP under the hood
                  }));
              
                  const link = document.createElement('a');
                  link.href = url;
                  link.download = chapterTitle + '.cbz'; // You can make this dynamic
                  document.body.appendChild(link);
                  link.click();
                  link.remove();
                  window.URL.revokeObjectURL(url);
            })
            .catch((ex) => {
                console.error(ex);
            })
            .finally(() => {
                setDownloadingChapters((prevSet) => {
                    const newSet = new Set(prevSet);
                    newSet.delete(chapterTitle);
                    return newSet;
                });
            });
    };

    return (
        <div className="chapters-container">
            <h2 className="chapters-heading">📖 Available Chapters</h2>
            <h2 className="chapters-heading">{title}</h2>

            {loading ? (
                <div className="spinner-container">
                    <div className="spinner"></div>
                    <p>Loading chapters...</p>
                </div>
            ) : (
                <div className="chapters-grid">
                    {Object.entries(data).map(([chapterTitle, details]) => (
                        <div
                            key={chapterTitle}
                            className="chapter-card"
                            onClick={() =>
                                !downloadingChapters.has(chapterTitle) &&
                                handleChapterClick(chapterTitle, details.url)
                            }
                            style={{
                                pointerEvents: downloadingChapters.has(chapterTitle) ? 'none' : 'auto',
                                opacity: downloadingChapters.has(chapterTitle) ? 0.6 : 1
                            }}
                        >
                            <h4 className="chapter-card-title">{chapterTitle}</h4>
                            <p className="chapter-card-subtitle">{processDate(details.release_date)}</p>
                            <p className="chapter-card-subtitle">
                                {downloadingChapters.has(chapterTitle) ? (
                                    <span className="spinner-small"></span>
                                ) : (
                                    "Download CBZ ⬇"
                                )}
                            </p>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}

export default Chapters;
