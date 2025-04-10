
const QuizData = {
    [1]: {
        ["Body"]: "Question1",
        ["Name"]: "Energy Consumption"
    },

    [2]: {
        ["Body"]: "Question2",
        ["Name"]: "Gas Usage"
    },

    [3]: {
        ["Body"]: "Question3",
        ["Name"]: "Miles Driven"
    },

    [4]: {
        ["Body"]: "Question4",
        ["Name"]: "Beef Consumption"
    },

    [5]: {
        ["Body"]: "Question5",
        ["Name"]: "Waste And Recycling"
    },

    [6]: {
        ["Body"]: "Question6",
        ["Name"]: "Water Usage"
    }
}

function ReturnStepData(Step) {
    return [QuizData[Step], document.getElementById(QuizData[Step].Body)];
}

function Hidden(Step, Toggle) {
    var [Data, Body] = ReturnStepData(Step)

    if (Toggle) {
        Body.setAttribute("hidden", true);
    } else {
        Body.removeAttribute("hidden");
    }
}

function checkAnswerAndEnableNext(Step) {
    const inputElements = document.querySelectorAll(`#Question${Step} input, #Question${Step} select`);
    const isAnswered = Array.from(inputElements).every(input => {
        // For select elements, check if a value is selected
        if (input.tagName === 'SELECT') {
            return input.value !== "";
        }
        // For input elements, check if a value is entered
        return input.value.trim() !== "";
    });

    const nextButton = document.getElementById("NextPage");
    if (isAnswered) {
        nextButton.removeAttribute("disabled");
    } else {
        nextButton.setAttribute("disabled", true);
    }
}

const QuizProgress = document.getElementById("QuizProgress");
const StepCounter = document.getElementById("Step-Counter");
const SectionText = document.getElementById("SectionText");
const Questions = Object.keys(QuizData).length

function UpdateStep(Step) {
    for (const [key, value] of Object.entries(QuizData)) { Hidden(key, true); }

    Hidden(Step, false);
    var [Data, Body] = ReturnStepData(Step);
    QuizProgress.style.width = `${(Step / Questions) * 100}%`;
    StepCounter.textContent = `Step ${Step} of ${ Questions }: ${Data.Name}`;
    SectionText.textContent = `${Data.Name}`;

    // Check if the current step has a valid answer
    checkAnswerAndEnableNext(Step);
}

const inputElements = document.querySelectorAll('select, input');
inputElements.forEach(input => {
    input.addEventListener('change', (event) => {
        // Find which step we are on
        const step = parseInt(event.target.closest('[id^="Question"]').id.replace('Question', ''));
        checkAnswerAndEnableNext(step);
    });
});

let CurrentStep = 1
UpdateStep(CurrentStep)

const NextPage = document.getElementById("NextPage")
const PreviousPage = document.getElementById("PreviousPage")

NextPage.onclick = () => {
    if (QuizData[CurrentStep+1] == null) {
        Results()
    }
    CurrentStep+=1;
    UpdateStep(CurrentStep);

    if (QuizData[CurrentStep+1] == null) {
        NextPage.textContent = "Results"
    } else {
        PreviousPage.removeAttribute("hidden")
    }
}

PreviousPage.onclick = () => {
    if (QuizData[CurrentStep-1] == null) {return}
    CurrentStep-=1;
    UpdateStep(CurrentStep);

    if (QuizData[CurrentStep-1] == null) {
        PreviousPage.setAttribute("hidden", true)
    } else {
        NextPage.removeAttribute("hidden")
    }
}

document.getElementById("Retry").onclick = () => {
    location.reload();
}

function Results(){
    document.getElementById("Questioner").setAttribute("hidden", true)
    document.getElementById("Results").removeAttribute("hidden");

    const electricity = document.getElementById("electricityUsage").value;
    const drives = document.getElementById("DrivenDistance").value;
    const beef = parseFloat(document.getElementById("BeefConsumption").value) || 0;
    const recycle = parseFloat(document.getElementById("RecyclePercentage").value) || 0;
    const water = parseFloat(document.getElementById("WaterUsage").value) || 0;

    let totalCO2 = 0;

    let electricity_kWh = 0;
    if (electricity.includes("Less than 100")) electricity_kWh = 75;
    else if (electricity.includes("100-249")) electricity_kWh = 175;
    else if (electricity.includes("250-399")) electricity_kWh = 325;
    else if (electricity.includes("400-599")) electricity_kWh = 500;
    else if (electricity.includes("600-900")) electricity_kWh = 750;
    else electricity_kWh = 1100;
    let elec_weekly = (electricity_kWh / 4);
    totalCO2 += elec_weekly * 0.233;

    let miles = 0;
    if (drives.includes("Less than 50")) miles = 25;
    else if (drives.includes("50–99")) miles = 75;
    else if (drives.includes("100–149")) miles = 125;
    else if (drives.includes("150–199")) miles = 175;
    else if (drives.includes("200–299")) miles = 250;
    else if (drives.includes("More than 300")) miles = 350;
    totalCO2 += miles * 0.28;


    totalCO2 += beef * 27;
    totalCO2 += water * 0.00137 * 7;
    let recycleReduction = (recycle > 80) ? 0.2 : (recycle / 100 * 0.2);
    totalCO2 *= (1 - recycleReduction);

    for (const [key, value] of Object.entries(QuizData)) { Hidden(key, true); }
    PreviousPage.setAttribute("hidden", true);
    NextPage.setAttribute("hidden", true);

    const ResultsList = document.getElementById("ResultsList");
    ResultsList.innerHTML = `
      <li class="list-group-item">Electricity: ${(elec_weekly * 0.233).toFixed(2)} kg CO₂/week</li>
      <li class="list-group-item">Driving: ${(miles * 0.28).toFixed(2)} kg CO₂/week</li>
      <li class="list-group-item">Beef Consumption: ${(beef * 27).toFixed(2)} kg CO₂/week</li>
      <li class="list-group-item">Water Usage: ${(water * 0.00137 * 7).toFixed(2)} kg CO₂/week</li>
      <li class="list-group-item text-success">Recycling Impact: -${(recycleReduction * 100).toFixed(1)}% reduction</li>
    `;

    const ResultsBar = document.getElementById("ResultsBar");
    const ResultsLevel = document.getElementById("ResultsLevel");
    let color = "bg-success";
    let level = "Low";

    if (totalCO2 > 100) {
        color = "bg-warning";
        level = "Moderate";
    }
    if (totalCO2 > 200) {
        color = "bg-danger";
        level = "High";
    }

    ResultsBar.style.width = `${Math.min(totalCO2, 300) / 3}%`;
    ResultsBar.className = `progress-bar ${color}`;
    ResultsLevel.textContent = `${level} Impact (~${totalCO2.toFixed(2)} kg CO₂/week)`;

    fetch('/submit_carbon', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            date: new Date().toISOString().split("T")[0], // "YYYY-MM-DD"
            emissions: totalCO2.toFixed(2),
            notes: `Electricity: ${(elec_weekly * 0.233).toFixed(2)}, Driving: ${(miles * 0.28).toFixed(2)}, Beef: ${(beef * 27).toFixed(2)}, Water: ${(water * 0.00137 * 7).toFixed(2)}, Recycle: -${(recycleReduction * 100).toFixed(1)}%`
        })
    })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                console.log("✅ Carbon result submitted successfully");
            } else {
                console.error("❌ Failed to save carbon result");
            }
        })
        .catch(error => {
            console.error("❌ Error submitting carbon result:", error);
        });

};
