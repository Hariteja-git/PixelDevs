let finalCodeStore = "";
let currentAgent = null;
let currentTimeout = null;


const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

async function startProcess() {
    const task = document.getElementById("taskInput").value;
    const lang = document.getElementById("langInput").value;
    const btn = document.getElementById("startBtn");

    if (!task.trim()) {
        alert("Enter a task first.");
        return;
    }

    
    resetAll();
    currentAgent = null;
    finalCodeStore = "";

    btn.disabled = true;
    btn.innerText = " Running Workflow...";

    const outputDeck = document.getElementById("outputDeck");
    outputDeck.style.display = "none";
    document.getElementById("finalCode").innerText = "Waiting for agents...";

    try {
        const response = await fetch(
            `/run_stream?task=${encodeURIComponent(task)}&language=${encodeURIComponent(lang)}`
        );

        if (!response.body) {
            throw new Error("Streaming not supported by browser.");
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value);
            const lines = chunk.split("\n");

            for (const line of lines) {
                if (!line.trim()) continue;

                try {
                    const data = JSON.parse(line);

                    if (data.error) {
                        alert("Server Error: " + data.error);
                        continue;
                    }

                    
                    handleEvent(data);
                    
                    
                    await delay(4000);

                } catch (err) {
                    console.error("JSON parse error:", err);
                }
            }
        }

        
        await delay(3000);

        
        btn.disabled = false;
        btn.innerText = " Initialize Agents";

        outputDeck.style.display = "block";

        if (finalCodeStore) {
            document.getElementById("finalCode").innerText = finalCodeStore;
        }

    } catch (error) {
        console.error(error);
        alert("Connection Error. Check console.");

        btn.disabled = false;
        btn.innerText = " Initialize Agents";
    }
}

function handleEvent(data) {
    const agent = data.agent;
    const status = data.status;
    const code = data.code;

    const el = document.getElementById(`agent-${agent}`);
    if (!el) return;

    
    if (currentTimeout) {
        clearTimeout(currentTimeout);
        currentTimeout = null;
    }

    
    if (currentAgent && currentAgent !== el) {
        currentAgent.classList.remove("active", "talking", "working");
    }

    currentAgent = el;

    
    el.classList.add("active");
    el.classList.add("talking");

    currentTimeout = setTimeout(() => {
        el.classList.remove("talking");
        el.classList.add("working");

        const termBody = el.querySelector(".term-body");
        termBody.innerText = `> Establishing Link...\n> ${status}`;

        if (agent === "Developer" && code) {
            finalCodeStore = code;

            const snippet = code.substring(0, 200).replace(/\n/g, " ");
            
            
            termBody.innerText = `> Establishing Link...\n> ${status}\n`; 

            typeWriter(
                termBody,
                `\n> CODE GENERATED:\n> ${snippet}...\n> [EOF]`
            );
        }

    }, 1000); 
}

function resetAll() {
    document.querySelectorAll(".agent-wrapper").forEach(el => {
        el.classList.remove("active", "talking", "working");

        const termBody = el.querySelector(".term-body");
        if (termBody) {
            termBody.innerText = "Waiting...";
        }
    });

    if (currentTimeout) {
        clearTimeout(currentTimeout);
        currentTimeout = null;
    }
}

function typeWriter(element, text) {
    let i = 0;
    
    
    function type() {
        if (i < text.length) {
            element.innerText += text.charAt(i);
            i++;
            setTimeout(type, 15);
        }
    }

    type();
}

function downloadCode() {
    if (!finalCodeStore) {
        alert("No code generated yet!");
        return;
    }

    const blob = new Blob([finalCodeStore], { type: "text/plain" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "generated_project.txt";
    a.click();
}