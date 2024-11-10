document.addEventListener("DOMContentLoaded", () => {
    // Typewriter effect for CLI commands
    const text = [
        "$ python Spotify.py",
        "Enter Spotify playlist URL (or 'exit' to quit): {playlist_url}",
        "Downloading tracks... [██████████] 100%",
    ];
    let line = 0;

    function typeLine() {
        if (line < text.length) {
            const pre = document.createElement("pre");
            pre.textContent = text[line++];
            document.querySelector(".cli-example").appendChild(pre);
            setTimeout(typeLine, 1000);
        }
    }

    typeLine();
});
