document.addEventListener("DOMContentLoaded", () => {
    // Typewriter effect for CLI commands
    const text = [
        "$ hackify download <playlist_url>",
        "Fetching playlist... Done",
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
