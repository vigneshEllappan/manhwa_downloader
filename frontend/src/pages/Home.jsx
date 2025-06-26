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
        "Reincarnated Murim Lord",
        "SwordMaster's Youngest Son",
        "The Regressed Mercenary's Machinations",
        "Duke's Eldest Son is a Regressed Hero",
        "Eternally Regressing Knight",
        "Legend of The Northern Blade",
        "Legendary Youngest Son of the Marquis House",
        "Top Tier Providence: Secretly Cultivate for a Thousand Years"
    ]
    const navigate = useNavigate();
    const handleClick = (title) => {
        navigate(`/chapterList/${title}`)
    }
    return (
        <div className="home-container">
            <h2 className="home-heading">📚 Available Manhwa</h2>
            <div className="home-grid">
                {manhwaList.map((title, index) => (
                    <div
                        key={index}
                        className="home-card"
                        onClick={() => handleClick(title)}
                    >
                        <h3 className="home-card-title">{title}</h3>
                        <p className="home-card-subtitle">View chapters ➜</p>
                    </div>
                ))}
            </div>
        </div>
    )
}

export default Home;