import React from "react";
import { useNavigate } from "react-router-dom";

function Home() {
    const manhwaList = [
        "Regressor of the Fallen Family",
        "Release That Witch",
        "Magic Emperor",
        "Descended From Divinity",
        "Regressed Life of The Sword Clan's Ignoble Reincarnator",
        "The Greatest Estate Developer",
        "Reincarnated Murim Lord"
    ]
    const navigate = useNavigate();
    const handleClick = (title) => {
        navigate(`/${title}/chapters`)
    }
    return (
        <React.Fragment>
            <h2>Available Manhwa's</h2>
            <ul>
                {manhwaList.map((content, index) => (
                    <li
                        key={index}
                        onClick={() => handleClick(content)}
                        style={{ cursor: 'pointer', color: 'blue' }}
                    >{content}</li>
                ))}
            </ul>
        </React.Fragment>
    )
}

export default Home;