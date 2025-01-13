// SIP Calculator
function calculateSIP() {
    const monthlyInvestment = document.getElementById('monthly_investment').value;
    const expectedReturn = document.getElementById('expected_return').value;
    const years = document.getElementById('years').value;

    fetch('/finance/sip-calculator', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            monthly_investment: monthlyInvestment,
            expected_return: expectedReturn,
            years: years
        })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('total_investment').textContent = data.total_investment;
        document.getElementById('total_returns').textContent = data.total_returns;
        document.getElementById('final_amount').textContent = data.final_amount;
    })
    .catch(error => console.error('Error:', error));
}

// Expense Chart
function createExpenseChart(data) {
    console.log('Creating chart with data:', data);
    const categories = Object.keys(data.breakdown);
    if (categories.length === 0) {
        console.log('No expense data found');
        document.getElementById('expense-chart').innerHTML = '<div class="alert alert-info">No expenses recorded yet. Add some expenses to see the breakdown.</div>';
        return;
    }
    
    const values = categories.map(cat => data.breakdown[cat].amount);
    const percentages = categories.map(cat => data.breakdown[cat].percentage.toFixed(1));
    
    const trace = {
        labels: categories.map((cat, i) => `${cat} (${percentages[i]}%)`),
        values: values,
        type: 'pie',
        hole: 0.4,
        marker: {
            colors: [
                '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', 
                '#9966FF', '#FF9F40', '#FF6384', '#36A2EB'
            ]
        },
        textinfo: 'label+percent',
        hoverinfo: 'label+value+percent',
        textposition: 'outside'
    };

    const layout = {
        height: 450,
        width: null, // This allows the chart to be responsive
        title: {
            text: 'Expense Breakdown',
            font: { size: 20 }
        },
        autosize: true,
        showlegend: true,
        legend: {
            orientation: 'h',
            y: -0.1
        },
        annotations: [{
            font: { size: 16, color: '#333' },
            showarrow: false,
            text: `Total: ₹${data.total_spent.toFixed(2)}`,
            x: 0.5,
            y: 0.5
        }],
        margin: { t: 50, l: 0, r: 0, b: 50 }
    };

    const config = {
        responsive: true,
        displayModeBar: false,
        displaylogo: false,
        modeBarButtonsToRemove: ['zoom2d', 'pan2d', 'select2d', 'lasso2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d', 'resetScale2d']
    };

    console.log('Plotting chart with trace:', trace);
    Plotly.newPlot('expense-chart', [trace], layout, config).then(() => {
        console.log('Chart plotted successfully');
    }).catch(error => {
        console.error('Error plotting chart:', error);
    });
}

function handleCategoryChange(select) {
    const customInput = document.getElementById('custom-category-input');
    if (select.value === 'custom') {
        customInput.style.display = 'block';
    } else {
        customInput.style.display = 'none';
    }
}

// Add or Update Expense
function addExpense(form) {
    const formData = new FormData(form);
    let category = formData.get('category');
    
    if (category === 'custom') {
        const customCategory = document.getElementById('custom-category').value.trim();
        if (!customCategory) {
            alert('Please enter a custom category');
            return false;
        }
        category = customCategory;
    }
    
    const expenseData = {
        amount: formData.get('amount'),
        category: category,
        description: formData.get('description')
    };

    const expenseId = form.dataset.expenseId;
    const isEdit = !!expenseId;
    const url = isEdit ? `/finance/expenses/${expenseId}` : '/finance/expenses';
    const method = isEdit ? 'PUT' : 'POST';

    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(expenseData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            location.reload();
        }
    })
    .catch(error => console.error('Error:', error));
    return false;
}

// Reset form after submission
function resetForm(form) {
    form.reset();
    delete form.dataset.expenseId;
    const submitBtn = form.querySelector('button[type="submit"]');
    submitBtn.textContent = 'Add Expense';
    document.getElementById('custom-category-input').style.display = 'none';
}

// Financial Advice
async function getFinancialAdvice(topic) {
    const response = await fetch(`/finance/advice?topic=${encodeURIComponent(topic)}`);
    const data = await response.json();
    document.getElementById('advice-content').textContent = data.advice;
}

// Edit expense
function editExpense(id, category, amount, description) {
    // Update the current form to be an edit form
    const form = document.querySelector('.expense-form');
    form.dataset.expenseId = id;
    
    // Fill in the form with current values
    document.getElementById('amount').value = amount;
    document.getElementById('category').value = category;
    document.getElementById('description').value = description;
    
    // Change submit button text
    const submitBtn = form.querySelector('button[type="submit"]');
    submitBtn.textContent = 'Update Expense';
    
    // Scroll to form
    form.scrollIntoView({ behavior: 'smooth' });
}

// Delete expense
function deleteExpense(id) {
    if (!confirm('Are you sure you want to delete this expense?')) {
        return;
    }
    
    fetch(`/finance/expenses/${id}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            location.reload();
        }
    })
    .catch(error => console.error('Error:', error));
}

// Load expense chart on page load
window.addEventListener('load', function() {
    const chartContainer = document.getElementById('expense-chart');
    if (chartContainer) {
        fetch('/finance/expenses/analysis')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                console.log('Received data:', data);
                if (!data || !data.breakdown) {
                    chartContainer.innerHTML = '<div class="alert alert-info">No expense data available</div>';
                    return;
                }
                createExpenseChart(data);
            })
            .catch(error => console.error('Error loading expense data:', error));
    }
});

// Create Goal
function createGoal(form) {
    const formData = new FormData(form);
    fetch('/finance/goals', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(Object.fromEntries(formData))
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            location.reload();
        }
    })
    .catch(error => console.error('Error:', error));
    return false;
}
