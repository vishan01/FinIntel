// SIP Calculator
function calculateSIP() {
    const monthlyInvestment = document.getElementById('monthly_investment').value;
    const expectedReturn = document.getElementById('expected_return').value;
    const years = document.getElementById('years').value;

    // Convert input values to numbers before sending
    fetch('/finance/sip-calculator', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
        },
        body: JSON.stringify({
            monthly_investment: parseFloat(monthlyInvestment),
            expected_return: parseFloat(expectedReturn),
            years: parseInt(years)
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        // Format numbers with commas and 2 decimal places
        document.getElementById('total_investment').textContent = 
            Number(data.total_investment).toLocaleString('en-IN', {maximumFractionDigits: 2});
        document.getElementById('total_returns').textContent = 
            Number(data.total_returns).toLocaleString('en-IN', {maximumFractionDigits: 2});
        document.getElementById('final_amount').textContent = 
            Number(data.final_amount).toLocaleString('en-IN', {maximumFractionDigits: 2});
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Failed to calculate SIP. Please try again.');
    });
}
function createExpenseTrendChart(monthlyData) {
    console.log('Creating trend chart with monthly data:', monthlyData);
    const months = monthlyData.map(d => d.month);
    const amounts = monthlyData.map(d => d.amount);

    // Calculate moving average for trend line
    const movingAverage = [];
    const period = 3; // 3-month moving average
    
    for (let i = 0; i < amounts.length; i++) {
        if (i < period - 1) {
            movingAverage.push(null);
            continue;
        }
        
        let sum = 0;
        for (let j = 0; j < period; j++) {
            sum += amounts[i - j];
        }
        movingAverage.push(sum / period);
    }

    const traces = [
        {
            x: dates,
            y: amounts,
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Monthly Expenses',
            line: {
                color: '#0d6efd',
                width: 2
            },
            marker: {
                size: 8,
                color: '#0d6efd'
            },
            hovertemplate: 'Month: %{x}<br>Amount: ₹%{y:.2f}<extra></extra>'
        },
        {
            x: months,
            y: movingAverage,
            type: 'scatter',
            mode: 'lines',
            name: '3-Month Trend',
            line: {
                color: '#dc3545',
                width: 2,
                dash: 'dot'
            },
            hovertemplate: 'Month: %{x}<br>Trend: ₹%{y:.2f}<extra></extra>'
        }
    ];

    const layout = {
        height: 400,
        width: null,
        title: {
            text: 'Monthly Expense Trend (Last 12 Months)',
            font: { size: 20 }
        },
        xaxis: {
            title: 'Month',
            tickangle: -45,
            tickmode: 'array',
            ticktext: months,
            tickvals: months,
            showgrid: true,
            gridcolor: '#f0f0f0'
        },
        yaxis: {
            title: 'Total Expenses (₹)',
            tickformat: ',.0f',
            showgrid: true,
            gridcolor: '#f0f0f0'
        },
        showlegend: true,
        legend: {
            orientation: 'h',
            y: -0.2
        },
        autosize: true,
        margin: { 
            t: 50,
            l: 80,
            r: 20,
            b: 120  // Increased bottom margin for rotated labels
        },
        plot_bgcolor: 'white'
    };

    const config = {
        responsive: true,
        displayModeBar: false,
        displaylogo: false
    };

    try {
        Plotly.newPlot('expense-trend', traces, layout, config).then(() => {
            console.log('Trend chart plotted successfully');
        }).catch(error => {
            console.error('Error plotting trend chart:', error);
        });
    } catch (error) {
        console.error('Error creating trend chart:', error);
        document.getElementById('expense-trend').innerHTML = 
            '<div class="alert alert-danger">Error creating expense trend chart</div>';
    }
}
// Expense Chart
// Expense Chart Functions
function createExpenseChart(data) {
    console.log('Creating pie chart with data:', data);
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
        height: 400,
        width: null, // This allows the chart to be responsive
        title: {
            text: '',  // Title is now in the HTML
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
    try {
        Plotly.newPlot('expense-chart', [trace], layout, config).then(() => {
            console.log('Pie chart plotted successfully');
        }).catch(error => {
            console.error('Error plotting pie chart:', error);
        });
    } catch (error) {
        console.error('Error creating pie chart:', error);
        document.getElementById('expense-chart').innerHTML = 
            '<div class="alert alert-danger">Error creating expense chart</div>';
    }
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
        date: formData.get('date'),
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
            'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
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

function editGoal(id, name, targetAmount, currentAmount, targetDate) {
    // Update form for editing
    const form = document.getElementById('goalForm');
    form.dataset.goalId = id;
    
    // Fill form fields
    document.getElementById('name').value = name;
    document.getElementById('target_amount').value = targetAmount;
    document.getElementById('current_amount').value = currentAmount || '';
    document.getElementById('target_date').value = targetDate;
    
    // Update submit button
    const submitBtn = document.getElementById('goalSubmitBtn');
    submitBtn.textContent = 'Update Goal';
    
    // Scroll to form
    form.scrollIntoView({ behavior: 'smooth' });
}

function deleteGoal(id) {
    if (!confirm('Are you sure you want to delete this goal?')) {
        return;
    }
    
    fetch(`/finance/goals/${id}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
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

// Update createGoal to handle both create and edit
function createGoal(form) {
    const formData = new FormData(form);
    const goalId = form.dataset.goalId;
    const isEdit = !!goalId;
    
    const data = {
        name: formData.get('name'),
        target_amount: formData.get('target_amount'),
        current_amount: formData.get('current_amount') || 0,
        target_date: formData.get('target_date')
    };
    
    const url = isEdit ? `/finance/goals/${goalId}` : '/finance/goals';
    const method = isEdit ? 'PUT' : 'POST';
    
    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
        },
        body: JSON.stringify(data)
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
    // Show loading spinner
    const loadingSpinner = document.getElementById('advice-loading');
    loadingSpinner.style.display = 'block';
    
    try {
        const response = await fetch(`/finance/advice_info/${topic}`);
        const data = await response.json();
        console.log(data);
        document.getElementById('advice-content').innerHTML = data;
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('advice-content').innerHTML = 'Sorry, there was an error getting financial advice.';
    } finally {
        // Hide loading spinner
        loadingSpinner.style.display = 'none';
    }
}

// Edit expense
function editExpense(id, category, amount, description, date) {
    // Update the current form to be an edit form
    const form = document.querySelector('.expense-form');
    form.dataset.expenseId = id;
    
    // Fill in the form with current values
    document.getElementById('date').value = date;
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
            'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
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
    // Set default date to today
    const today = new Date().toISOString().split('T')[0];
    const dateInput = document.getElementById('date');
    if (dateInput) {
        dateInput.value = today;
        dateInput.max = today; // Prevent future dates
    }

    console.log('Loading expense charts...');
    const chartContainer = document.getElementById('expense-chart');
    const histogramContainer = document.getElementById('expense-trend');
    
    if (chartContainer && histogramContainer) {
        fetch('/finance/expenses/analysis')
            .then(response => {
                console.log('Got response from server');
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
                
                // Create pie chart
                
                createExpenseChart(data);
                // Create line chart if we have trend data
                if (data.monthly_trend && data.monthly_trend.length > 0) {
                    console.log('Creating trend chart with data:', data.monthly_trend);
                    createExpenseTrendChart(data.monthly_trend);
                } else {
                    console.log('No trend data available');
                    document.getElementById('expense-trend').innerHTML = 
                        '<div class="alert alert-info">No trend data available</div>';
                }
            })
            .catch(error => {
                console.error('Error loading expense data:', error);
                chartContainer.innerHTML = '<div class="alert alert-danger">Error loading expense chart</div>';
                histogramContainer.innerHTML = '<div class="alert alert-danger">Error loading expense trend</div>';
            });
    } else {
        console.error('Chart containers not found');
    }
});

function createExpenseTrendChart(monthlyData) {
    console.log('Creating trend chart with monthly data:', monthlyData);
    const months = monthlyData.map(d => d.month);
    const amounts = monthlyData.map(d => d.amount);

    // Calculate moving average for trend line
    const movingAverage = [];
    const period = 3; // 3-month moving average
    
    for (let i = 0; i < amounts.length; i++) {
        if (i < period - 1) {
            movingAverage.push(null);
            continue;
        }
        
        let sum = 0;
        for (let j = 0; j < period; j++) {
            sum += amounts[i - j];
        }
        movingAverage.push(sum / period);
    }

    const traces = [
        {
            x: months,
            y: amounts,
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Monthly Expenses',
            line: {
                color: '#0d6efd',
                width: 2
            },
            marker: {
                size: 8,
                color: '#0d6efd'
            },
            hovertemplate: 'Month: %{x}<br>Amount: ₹%{y:.2f}<extra></extra>'
        },
        {
            x: months,
            y: movingAverage,
            type: 'scatter',
            mode: 'lines',
            name: '3-Month Trend',
            line: {
                color: '#dc3545',
                width: 2,
                dash: 'dot'
            },
            hovertemplate: 'Month: %{x}<br>Trend: ₹%{y:.2f}<extra></extra>'
        }
    ];

    const layout = {
        height: 400,
        width: null,
        title: {
            text: '',  // Title is now in the HTML
            font: { size: 20 }
        },
        xaxis: {
            title: 'Month',
            tickangle: -45,
            showgrid: true,
            gridcolor: '#f0f0f0'
        },
        yaxis: {
            title: 'Total Expenses (₹)',
            tickformat: ',.0f',
            showgrid: true,
            gridcolor: '#f0f0f0'
        },
        showlegend: true,
        legend: {
            orientation: 'h',
            y: -0.2
        },
        autosize: true,
        margin: { 
            t: 50,
            l: 80,
            r: 20,
            b: 100
        },
        plot_bgcolor: 'white'
    };

    const config = {
        responsive: true,
        displayModeBar: false,
        displaylogo: false
    };

    try {
        Plotly.newPlot('expense-trend', traces, layout, config).then(() => {
            console.log('Trend chart plotted successfully');
        }).catch(error => {
            console.error('Error plotting trend chart:', error);
        });
    } catch (error) {
        console.error('Error creating trend chart:', error);
        document.getElementById('expense-trend').innerHTML = 
            '<div class="alert alert-danger">Error creating expense trend chart</div>';
    }
}

// Goal Management
function createGoal(form) {
    const formData = new FormData(form);
    fetch('/finance/goals', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
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
    window.location.reload()
    console.log("done")
    return false;
}
