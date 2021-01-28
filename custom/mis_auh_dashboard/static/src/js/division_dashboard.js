odoo.define('DivisionDashboard.DivisionDashboard', function (require) {
    'use strict';
    var AbstractAction = require('web.AbstractAction');
    var ajax = require('web.ajax');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var web_client = require('web.web_client');
    var _t = core._t;
    var QWeb = core.qweb;
    var self = this;
    var currency;
    var ActionMenu = AbstractAction.extend({

        template: 'Divisiondashboard',

        events: {
            'click .division_dashboard': 'onclick_dashboard',
            'click #mbk_group': 'onclick_mbk_group',
            'change #division_values': 'onclick_division',
        },
        onclick_mbk_group: function (ev) {
            document.getElementById("mbk_group").style.color = "red";
            document.getElementById("adwv").style.color = "black";
        },
        onclick_adwv: function (ev) {
            document.getElementById("adwv").style.color = "red";
            document.getElementById("mbk_group").style.color = "black";
        },

        onclick_division: function (e) {
            e.stopPropagation();
                var $target = $(e.target);
                var value = $target.val();
            if (value=="0") {
                document.getElementById("logo").src = "/mis_auh_dashboard/static/description/logo.jpg";
                document.getElementById("logo").width = "80"
                document.getElementById("logo").height = "100"
            } else if (value=="9"){
                document.getElementById("logo").src = "/mis_auh_dashboard/static/description/adwv.png";
                document.getElementById("logo").width = "204"
                document.getElementById("logo").height = "100"
            } else if (value=="10"){
                document.getElementById("logo").src = "/mis_auh_dashboard/static/description/adpm.png";
                document.getElementById("logo").width = "143"
                document.getElementById("logo").height = "100"
            } else if (value=="11"){
                document.getElementById("logo").src = "/mis_auh_dashboard/static/description/mbks.png";
                document.getElementById("logo").width = "95"
                document.getElementById("logo").height = "100"
            } else if (value=="12"){
                document.getElementById("logo").src = "/mis_auh_dashboard/static/description/rmad.jpg";
                document.getElementById("logo").width = "83"
                document.getElementById("logo").height = "100"
            } else if (value=="13"){
                document.getElementById("logo").src = "/mis_auh_dashboard/static/description/rmfj.jpg";
                document.getElementById("logo").width = "116"
                document.getElementById("logo").height = "100"
            } else if (value=="14"){
                document.getElementById("logo").src = "/mis_auh_dashboard/static/description/utab.jpg";
                document.getElementById("logo").width = "200"
                document.getElementById("logo").height = "65"
            } else if (value=="15"){
                document.getElementById("logo").src = "/mis_auh_dashboard/static/description/utfj.jpg";
                document.getElementById("logo").width = "200"
                document.getElementById("logo").height = "65"
            } else if (value=="16"){
                document.getElementById("logo").src = "/mis_auh_dashboard/static/description/fjml.jpg";
                document.getElementById("logo").width = "124"
                document.getElementById("logo").height = "100"
            } else if (value=="17"){
                document.getElementById("logo").src = "/mis_auh_dashboard/static/description/glxc.jpg";
                document.getElementById("logo").width = "185"
                document.getElementById("logo").height = "100"
            } else if (value=="18"){
                document.getElementById("logo").src = "/mis_auh_dashboard/static/description/shct.jpg";
                document.getElementById("logo").width = "200"
                document.getElementById("logo").height = "80"
            } else {
                document.getElementById("logo").src = "/mis_auh_dashboard/static/description/logo_missing.png";
                document.getElementById("logo").width = "100"
                document.getElementById("logo").height = "100"
            }

            rpc.query({
                        model: "account.move",
                        method: "get_division_profit",
                        args: [value],
                    })
                        .then(function (result) {
                            currency = 'AED'
                            var net_profit_this_year = result[0].pl_this_year;
                            var net_profit_this_months = result[0].pl_this_month;
                            var incomes_this_year = result[0].income_this_year;
                            var income_this_month = result[0].income_this_month;
                            var expenses_this_year = result[0].expense_this_year;
                            var expenses_this_month = result[0].expense_this_month;
                            var opl_this_year = result[0].opl_this_year;
                            var opl_this_month = result[0].opl_this_month;
                            var header = result[0].header;

                            function format_amount(amount){
                                 if (typeof(amount) != 'number'){
                                    amount = parseFloat(0.00);
                                 }
                                 var formatted_value = (parseInt(amount)).toLocaleString("en-US", {minimumFractionDigits: 2})
                                 return formatted_value += ' ' + "AED";
                            }

                            net_profit_this_year = format_amount(net_profit_this_year);
                            net_profit_this_months = format_amount(net_profit_this_months);
                            incomes_this_year = format_amount(incomes_this_year);
                            income_this_month = format_amount(income_this_month);
                            expenses_this_year = format_amount(expenses_this_year);
                            expenses_this_month = format_amount(expenses_this_month);
                            opl_this_year = format_amount(opl_this_year);
                            opl_this_month = format_amount(opl_this_month);

                             $('#net_profit_current_year').empty();
                             $('#net_profit_current_months').empty();
                             $('#opl_current_year').empty();
                             $('#opl_current_months').empty();
                             $('#total_incomes_this_year').empty();
                             $('#total_incomes_').empty();
                             $('#total_expense_this_year').empty();
                             $('#total_expenses_').empty();
                             $('#header1').empty();

                            $('#net_profit_current_year').append('<span>' + net_profit_this_year + '</span> <div class="title">This Year</div>')
                            $('#net_profit_current_months').append('<span>' + net_profit_this_months + '</span> <div class="title">This Month</div>')
                            $('#opl_current_year').append('<span>' + opl_this_year + '</span> <div class="title">This Year</div>')
                            $('#opl_current_months').append('<span>' + opl_this_month + '</span> <div class="title">This Month</div>')
                            $('#total_incomes_this_year').append('<span>' + incomes_this_year + '</span><div class="title">This Year</div>')
                            $('#total_incomes_').append('<span>' + income_this_month + '</span><div class="title">This month</div>')
                            $('#total_expense_this_year').append('<span >' + expenses_this_year + '</span><div class="title">This Year</div>')
                            $('#total_expenses_').append('<span>' + expenses_this_month + '</span><div class="title">This month</div>')
                            $('#header1').append('<span>' + header + '</span>')
                    })

            rpc.query({
                        model: "account.move",
                        method: "get_expense",
                        args: [value],
                    }).then(function (result) {
                            var due_count = 0;
                            var amount;
                            var total_amount = 0.00;
                            function format_amount(amount){
                                 if (typeof(amount) != 'number'){
                                    amount = parseFloat(0.00);
                                 }
                                 var formatted_value = (parseInt(amount)).toLocaleString("en-US", {minimumFractionDigits: 2})
                                 return formatted_value += ' ' + "AED";
                            }
                             $('#expense_list').empty();
                              $('#total_expense').empty();
                            _.forEach(result, function (x) {
                                $('#expense_list').show();
                                due_count++;
                                amount = format_amount(x.amount);
                                total_amount += x.amount
                                $('#expense_list').append('<li><div>' + x.particulars + '</div>' + '<div>' + amount + '</div>' + '</li>');
                            });
                            total_amount = format_amount(total_amount);
                            $('#total_expense').append('<span>' + total_amount + '</span>')
                        })

                   rpc.query({
                        model: "account.move",
                        method: "get_revenue",
                        args: [value],
                    }).then(function (result) {
                            var due_count = 0;
                            var amount;
                            var total_amount = 0.00;
                             $('#revenue_list').empty();
                             $('#total_revenue').empty();

                            function format_amount(amount){
                                 if (typeof(amount) != 'number'){
                                    amount = parseFloat(0.00);
                                 }
                                 var formatted_value = (parseInt(amount)).toLocaleString("en-US", {minimumFractionDigits: 2})
                                 return formatted_value += ' ' + "AED";
                            }
                            _.forEach(result, function (x) {
                                $('#revenue_list').show();
                                due_count++;
                                amount = format_amount(x.amount);
                                if (Math.abs(x.amount) > 0.05) {
                                    total_amount += x.amount
                                    $('#revenue_list').append('<li><div>' + x.particulars + '</div>' + '<div>' + amount + '</div>' + '</li>');
                                }
                            });
                            total_amount = format_amount(total_amount);
                            $('#total_revenue').append('<span>' + total_amount + '</span>')
                        })
                   rpc.query({
                        model: "account.move",
                        method: "get_division_income_expense",
                        args: [value],
                    })
                        .then(function (result) {
                            var pl_ctx = document.getElementById("pl_canvas").getContext('2d');
                            var income_ctx = document.getElementById("income_canvas").getContext('2d');
                            var expense_ctx = document.getElementById("expense_canvas").getContext('2d');
                            var opl_ctx = document.getElementById("opl_canvas").getContext('2d');
                            $('#canvas').empty();
                            $('#pl_canvas').empty();
                            $('#income_canvas').empty();
                            $('#expense_canvas').empty();
                            $('#opl_canvas').empty();

                            // Define the data
                            var income = result.income; // Add data values to array
                            var expense = result.expense;
                            var opl = result.opl;
                            var profit = result.profit;
                            var opl_table = result.opl_table;

                            var labels = result.month; // Add labels to array
                            var y_labels = result.y_labels; // Add labels to array

                            // End Defining data
                            if (window.myCharts != undefined)
                                window.myCharts.destroy();
                            window.myCharts = new Chart($("#canvas"), {
                                //var myChart = new Chart(ctx, {
                                type: 'bar',
                                data: {
                                    labels: labels,
                                    datasets: [{
                                        label: 'Income', // Name the series
                                        data: income, // Specify the data values array
                                        backgroundColor: '#66aecf',
                                        borderColor: '#66aecf',

                                        borderWidth: 1, // Specify bar border width
                                        type: 'bar', // Set this data to a line chart
                                        fill: false
                                    },
                                        {
                                            label: 'Expense', // Name the series
                                            data: expense, // Specify the data values array
                                            backgroundColor: '#fa9fb5',
                                            borderColor: '#fa9fb5',

                                            borderWidth: 1, // Specify bar border width
                                            type: 'bar', // Set this data to a line chart
                                            fill: false
                                        },
                                       {
                                            label: 'Operating Profit/Loss', // Name the series
                                            data: opl, // Specify the data values array
                                            backgroundColor: '#ffa600',
                                            borderColor: '#ffa600',

                                            borderWidth: 2, // Specify bar border width
                                            type: 'line', // Set this data to a line chart
                                            fill: false
                                        },
                                        {
                                            label: 'Profit/Loss', // Name the series
                                            data: profit, // Specify the data values array
                                            backgroundColor: '#0bd465',
                                            borderColor: '#0bd465',

                                            borderWidth: 2, // Specify bar border width
                                            type: 'line', // Set this data to a line chart
                                            fill: false
                                        }
                                    ]
                                },
                                options: {
                                    responsive: true, // Instruct chart js to respond nicely.
                                    maintainAspectRatio: false, // Add to prevent default behaviour of full-width/height
                                    scales: {
                                        yAxes: [{
                                            ticks: {
                                                beginAtZero: true
                                            }
                                        }]
                                    }
                                }
                            });

                            if (window.profitCharts != undefined)
                                window.profitCharts.destroy();
                            window.profitCharts = new Chart(pl_ctx, {
                                type: 'bar',
                                data: {
                                    labels: labels,
                                    datasets: [{
                                        label: 'Profit', // Name the series
                                        data: profit, // Specify the data values array
                                        backgroundColor: '#66aecf',
                                        borderColor: '#66aecf',

                                        borderWidth: 1, // Specify bar border width
                                        type: 'bar', // Set this data to a line chart
                                        fill: false
                                    },
                                    ]
                                },
                                options: {
                                    responsive: true, // Instruct chart js to respond nicely.
                                    maintainAspectRatio: false, // Add to prevent default behaviour of full-width/height
                                    scales: {
                                        yAxes: [{
                                            ticks: {
                                                beginAtZero: true
                                            }
                                        }]
                                    }
                                }
                            });

                            if (window.incomeCharts != undefined)
                               window.incomeCharts.destroy();
                            window.incomeCharts = new Chart(income_ctx, {
                                type: 'bar',
                                data: {
                                    labels: labels,
                                    datasets: [{
                                        label: 'Income', // Name the series
                                        data: income, // Specify the data values array
                                        backgroundColor: '#2ca25f',
                                        borderColor: '#2ca25f',

                                        borderWidth: 1, // Specify bar border width
                                        type: 'bar', // Set this data to a line chart
                                        fill: false
                                    },
                                    ]
                                },
                                options: {
                                    responsive: true, // Instruct chart js to respond nicely.
                                    maintainAspectRatio: false, // Add to prevent default behaviour of full-width/height
                                    scales: {
                                        yAxes: [{
                                            ticks: {
                                                beginAtZero: true
                                            }
                                        }]
                                    }
                                }
                            });

                            if (window.expenseCharts != undefined)
                                window.expenseCharts.destroy();
                            window.expenseCharts = new Chart(expense_ctx, {
                                type: 'bar',
                                data: {
                                    labels: labels,
                                    datasets: [{
                                        label: 'Expense', // Name the series
                                        data: expense, // Specify the data values array
                                        backgroundColor: '#fa9fb5',
                                        borderColor: '#fa9fb5',

                                        borderWidth: 1, // Specify bar border width
                                        type: 'bar', // Set this data to a line chart
                                        fill: false
                                    },
                                    ]
                                },
                                options: {
                                    responsive: true, // Instruct chart js to respond nicely.
                                    maintainAspectRatio: false, // Add to prevent default behaviour of full-width/height
                                    scales: {
                                        yAxes: [{
                                            ticks: {
                                                beginAtZero: true
                                            }
                                        }]
                                    }
                                }
                            });

                            if (window.oplCharts != undefined)
                                window.oplCharts.destroy();
                            window.oplCharts = new Chart(opl_ctx, {
                                type: 'line',
                                data: {
                                    labels: y_labels,
                                    datasets: [{
                                        label: 'Operating Profit/Loss', // Name the series
                                        data: opl_table, // Specify the data values array
                                        backgroundColor: '#ffa600',
                                        borderColor: '#ffa600',

                                        borderWidth: 3, // Specify bar border width
                                        type: 'line', // Set this data to a line chart
                                        fill: false
                                    },
                                    ]
                                },
                                options: {
                                    responsive: true, // Instruct chart js to respond nicely.
                                    maintainAspectRatio: false, // Add to prevent default behaviour of full-width/height
                                    scales: {
                                        yAxes: [{
                                            ticks: {
                                                beginAtZero: true
                                            }
                                        }]
                                    }
                                }
                            });

                        })

                    },

        onclick_bank_balance: function (ev) {
            var posted = false;
            if ($('#toggle-two')[0].checked == true) {
                posted = "posted"
            rpc.query({
                model: "account.move",
                method: "get_currency",
            })
                .then(function (result) {
                    currency = result;
                })
            }
        },

        renderElement: function (ev) {
            var self = this;
            var f = 0;
            $.when(this._super())
                .then(function (ev) {

                    rpc.query({
                        model: "account.move",
                        method: "get_currency",
                    })
                        .then(function (result) {
                            currency = result;
                        })

                    rpc.query({
                        model: "account.move",
                        method: "get_expense",
                        args: [f],
                    }).then(function (result) {
                            var due_count = 0;
                            var amount;
                            var total_amount = 0.00;
                            _.forEach(result, function (x) {
                                $('#expense_list').show();
                                due_count++;
                                amount = self.format_currency(currency, x.amount);
                                total_amount += x.amount
                                $('#expense_list').append('<li><div>' + x.particulars + '</div>' + '<div>' + amount + '</div>' + '</li>');
                            });
                            total_amount = self.format_currency(currency, total_amount);
                            $('#total_expense').append('<span>' + total_amount + '</span>')
                        })

                    rpc.query({
                        model: "account.move",
                        method: "get_division_income_expense",
                        args: [f],
                    })
                        .then(function (result) {

                            var ctx = document.getElementById("canvas").getContext('2d');
                            var pl_ctx = document.getElementById("pl_canvas").getContext('2d');
                            var income_ctx = document.getElementById("income_canvas").getContext('2d');
                            var expense_ctx = document.getElementById("expense_canvas").getContext('2d');
                            var opl_ctx = document.getElementById("opl_canvas").getContext('2d');

                            // Define the data
                            var income = result.income; // Add data values to array
                            var expense = result.expense;
                            var opl = result.opl;
                            var profit = result.profit;
                            var opl_table = result.opl_table;
                            var labels = result.month; // Add labels to array
                            var y_labels = result.y_labels;
                            // End Defining data

                            // End Defining data
                            if (window.myCharts != undefined)
                                window.myCharts.destroy();
                            window.myCharts = new Chart(ctx, {
                                //var myChart = new Chart(ctx, {
                                type: 'bar',
                                data: {
                                    labels: labels,
                                    datasets: [{
                                        label: 'Income', // Name the series
                                        data: income, // Specify the data values array
                                        backgroundColor: '#66aecf',
                                        borderColor: '#66aecf',

                                        borderWidth: 1, // Specify bar border width
                                        type: 'bar', // Set this data to a line chart
                                        fill: false
                                    },
                                        {
                                            label: 'Expense', // Name the series
                                            data: expense, // Specify the data values array
                                            backgroundColor: '#fa9fb5',
                                            borderColor: '#fa9fb5',

                                            borderWidth: 1, // Specify bar border width
                                            type: 'bar', // Set this data to a line chart
                                            fill: false
                                        },
                                       {
                                            label: 'Operating Profit/Loss', // Name the series
                                            data: opl, // Specify the data values array
                                            backgroundColor: '#ffa600',
                                            borderColor: '#ffa600',

                                            borderWidth: 2, // Specify bar border width
                                            type: 'line', // Set this data to a line chart
                                            fill: false
                                        },
                                        {
                                            label: 'Profit/Loss', // Name the series
                                            data: profit, // Specify the data values array
                                            backgroundColor: '#0bd465',
                                            borderColor: '#0bd465',

                                            borderWidth: 2, // Specify bar border width
                                            type: 'line', // Set this data to a line chart
                                            fill: false
                                        }
                                    ]
                                },
                                options: {
                                    responsive: true, // Instruct chart js to respond nicely.
                                    maintainAspectRatio: false, // Add to prevent default behaviour of full-width/height
                                    scales: {
                                        yAxes: [{
                                            ticks: {
                                                beginAtZero: true
                                            }
                                        }]
                                    }
                                }
                            });

                            if (window.profitCharts != undefined)
                                window.profitCharts.destroy();
                            window.profitCharts = new Chart(pl_ctx, {
                                type: 'bar',
                                data: {
                                    labels: labels,
                                    datasets: [{
                                        label: 'Profit', // Name the series
                                        data: profit, // Specify the data values array
                                        backgroundColor: '#66aecf',
                                        borderColor: '#66aecf',

                                        borderWidth: 1, // Specify bar border width
                                        type: 'bar', // Set this data to a line chart
                                        fill: false
                                    },
                                    ]
                                },
                                options: {
                                    responsive: true, // Instruct chart js to respond nicely.
                                    maintainAspectRatio: false, // Add to prevent default behaviour of full-width/height
                                    scales: {
                                        yAxes: [{
                                            ticks: {
                                                beginAtZero: true
                                            }
                                        }]
                                    }
                                }
                            });

                            if (window.incomeCharts != undefined)
                                window.incomeCharts.destroy();
                            window.incomeCharts = new Chart(income_ctx, {
                                type: 'bar',
                                data: {
                                    labels: labels,
                                    datasets: [{
                                        label: 'Income', // Name the series
                                        data: income, // Specify the data values array
                                        backgroundColor: '#2ca25f',
                                        borderColor: '#2ca25f',

                                        borderWidth: 1, // Specify bar border width
                                        type: 'bar', // Set this data to a line chart
                                        fill: false
                                    },
                                    ]
                                },
                                options: {
                                    responsive: true, // Instruct chart js to respond nicely.
                                    maintainAspectRatio: false, // Add to prevent default behaviour of full-width/height
                                    scales: {
                                        yAxes: [{
                                            ticks: {
                                                beginAtZero: true
                                            }
                                        }]
                                    }
                                }
                            });

                            if (window.expenseCharts != undefined)
                                window.expenseCharts.destroy();
                            window.expenseCharts = new Chart(expense_ctx, {
                                type: 'bar',
                                data: {
                                    labels: labels,
                                    datasets: [{
                                        label: 'Expense', // Name the series
                                        data: expense, // Specify the data values array
                                        backgroundColor: '#fa9fb5',
                                        borderColor: '#fa9fb5',

                                        borderWidth: 1, // Specify bar border width
                                        type: 'bar', // Set this data to a line chart
                                        fill: false
                                    },
                                    ]
                                },
                                options: {
                                    responsive: true, // Instruct chart js to respond nicely.
                                    maintainAspectRatio: false, // Add to prevent default behaviour of full-width/height
                                    scales: {
                                        yAxes: [{
                                            ticks: {
                                                beginAtZero: true
                                            }
                                        }]
                                    }
                                }
                            });

                            if (window.oplCharts != undefined)
                                window.oplCharts.destroy();
                            window.oplCharts = new Chart(opl_ctx, {
                                type: 'line',
                                data: {
                                    labels: y_labels,
                                    datasets: [{
                                        label: 'Operating Profit/Loss', // Name the series
                                        data: opl_table, // Specify the data values array
                                        backgroundColor: '#ffa600',
                                        borderColor: '#ffa600',

                                        borderWidth: 3, // Specify bar border width
                                        type: 'line', // Set this data to a line chart
                                        fill: false
                                    },
                                    ]
                                },
                                options: {
                                    responsive: true, // Instruct chart js to respond nicely.
                                    maintainAspectRatio: false, // Add to prevent default behaviour of full-width/height
                                    scales: {
                                        yAxes: [{
                                            ticks: {
                                                beginAtZero: true
                                            }
                                        }]
                                    }
                                }
                            });

                        })

                    rpc.query({
                        model: "account.move",
                        method: "get_division_profit",
                         args: [f],
                    })
                        .then(function (result) {
                            var net_profit_this_year = result[0].pl_this_year;
                            var net_profit_this_months = result[0].pl_this_month;
                            var incomes_this_year = result[0].income_this_year;
                            var income_this_month = result[0].income_this_month;
                            var expenses_this_year = result[0].expense_this_year;
                            var expenses_this_month = result[0].expense_this_month;
                            var opl_this_year = result[0].opl_this_year;
                            var opl_this_month = result[0].opl_this_month;
                            var header = result[0].header;

                            net_profit_this_year = self.format_currency(currency, net_profit_this_year);
                            net_profit_this_months = self.format_currency(currency, net_profit_this_months);
                            incomes_this_year = self.format_currency(currency, incomes_this_year);
                            income_this_month = self.format_currency(currency, income_this_month);
                            expenses_this_year = self.format_currency(currency, expenses_this_year);
                            expenses_this_month = self.format_currency(currency, expenses_this_month);
                            opl_this_year = self.format_currency(currency, opl_this_year);
                            opl_this_month = self.format_currency(currency, opl_this_month);

                            $('#net_profit_current_year').append('<span>' + net_profit_this_year + '</span> <div class="title">This Year</div>')
                            $('#net_profit_current_months').append('<span>' + net_profit_this_months + '</span> <div class="title">This Month</div>')
                            $('#opl_current_year').append('<span>' + opl_this_year + '</span> <div class="title">This Year</div>')
                            $('#opl_current_months').append('<span>' + opl_this_month + '</span> <div class="title">This Month</div>')
                            $('#total_incomes_this_year').append('<span>' + incomes_this_year + '</span><div class="title">This Year</div>')
                            $('#total_incomes_').append('<span>' + income_this_month + '</span><div class="title">This month</div>')
                            $('#total_expense_this_year').append('<span >' + expenses_this_year + '</span><div class="title">This Year</div>')
                            $('#total_expenses_').append('<span>' + expenses_this_month + '</span><div class="title">This month</div>')
                            $('#header1').append('<span>' + header + '</span>')
                        })

                   rpc.query({
                        model: "account.move",
                        method: "get_revenue",
                        args: [f],
                    }).then(function (result) {
                            var due_count = 0;
                            var amount;
                            var total_amount = 0.00;
                            _.forEach(result, function (x) {
                                $('#revenue_list').show();
                                due_count++;
                                amount = self.format_currency(currency, x.amount);
                                if (Math.abs(x.amount) > 0.05) {
                                    total_amount += x.amount
                                    $('#revenue_list').append('<li><div>' + x.particulars + '</div>' + '<div>' + amount + '</div>' + '</li>');
                                }
                            });
                            total_amount = self.format_currency(currency, total_amount);
                            $('#total_revenue').append('<span>' + total_amount + '</span>')
                        })

                   rpc.query({
                        model: "account.move",
                        method: "get_share_change",
                    }).then(function (result) {
                            var due_count = 0;
                            var amount;
                            var total_amount = 0.00;
                            _.forEach(result, function (x) {
                                $('#share_list').show();
                                due_count++;
                                amount = self.format_currency(currency, x.amount);
                                total_amount += x.amount
                                 if (x.amount > 0.00) {
                                    $('#share_list').append('<li><div>' + x.percentage + '</div>' + '<div style= "color:#008000;">' + amount + '&#11205;</div></li>');
                                 } else if (x.amount<0.00) {
                                    $('#share_list').append('<li><div>' + x.percentage + '</div>' + '<div style= "color:#FF0000;">' + amount + '&#11206;</div></li>');
                                 } else {
                                    $('#share_list').append('<li><div>' + x.percentage + '</div>' + '<div style= "color:#808080;">' + amount + ' </div></li>');
                                 }
                            });
                            var f_total_amount = self.format_currency(currency, total_amount);
                            if (total_amount>0.00){
                                $('#total_share').append('<span style= "color:#008000;">' + f_total_amount + '</span>')
                            } else if(total_amount<0.00){
                                $('#total_share').append('<span style= "color:#FF0000;">' + f_total_amount + '</span>')
                            } else {
                                 $('#total_share').append('<span style= "color:#808080;">' + f_total_amount + '</span>')
                            }

                        })


                });
        },

        format_currency: function(currency, amount){
             if (typeof(amount) != 'number'){
                amount = 0.00;
             }
             var formatted_value = (parseInt(amount)).toLocaleString("en-US", {minimumFractionDigits: 2})
             return formatted_value += ' ' + "AED";
        },

        willStart: function () {
            var self = this;
            self.drpdn_show = false;
            return Promise.all([ajax.loadLibs(this), this._super()]);
        },
    });
    core.action_registry.add('division_dashboard', ActionMenu);

});