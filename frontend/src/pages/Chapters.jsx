import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { GetChapters } from '../REST';
function Chapters() {
    const { title } = useParams();
    const [data, setData] = useState({});

    useEffect(() => {
        GetChapters(title).then((response) => {
            setData(JSON.parse(response.data))
        }).catch(ex => {
            console.log(ex)
            setData({})
        })
    }, [title]);

    const handleChapterClick = (title, url) => {
        console.log(title)
        console.log(url);
    }
    return (
        <React.Fragment>
            <h2>Chapter List</h2>
            <ul>
                {Object.entries(data).map(([title, url]) => (
                    <li key={title} onClick={() => handleChapterClick(title, url)} style={{ cursor: 'pointer' }}>
                        {title}
                    </li>
                ))}
            </ul>
        </React.Fragment>
    )
}

export default Chapters;