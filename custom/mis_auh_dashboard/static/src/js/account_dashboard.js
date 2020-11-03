odoo.define('AccountingDashboard.AccountingDashboard', function (require) {
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

        template: 'Invoicedashboard',

        events: {
            'click .invoice_dashboard': 'onclick_dashboard',
            'click #prog_bar': 'onclick_prog_bar',
            'click #onclick_banks_balance': 'onclick_bank_balance',
            'click #income_this_month': 'onclick_income_this_month',
            'click #income_this_year': 'onclick_income_this_year',
            'click #total_aged_payable': 'onclick_total_aged_payable',
            'click #in_ex_bar_chart': 'onclick_in_ex_bar_chart',
            'click #aged_recevable_pie_chart': 'onclick_aged_recevable_pie_chart',
            'click #bank_balance_hide': 'onclick_bank_balance_hide',
            'click #cash_balance_hide': 'onclick_cash_balance_hide',
            'click #in_ex_hide': 'onclick_in_ex_hide',
            'click #aged_payable_hide': 'onclick_aged_payable_hide',
            'change #income_expense_values': function(e) {
                            e.stopPropagation();
                            var $target = $(e.target);
                            var value = $target.val();
                            this.$('.income_expense_values').empty();
                            this.onclick_income_this_year(this.$('#income_expense_values').val());
                                                        },
            'change #toggle-two': 'onclick_toggle_two',

        },
        onclick_toggle_two: function (ev) {

        },

        onclick_income_last_year: function (ev) {
            ev.preventDefault();
            var selected = $('.btn.btn-tool.income');
            var data = $(selected[0]).data();
            var posted = false;
            if ($('#toggle-two')[0].checked == true) {
                posted = "posted"
            }
            rpc.query({
                model: 'account.move',
                method: 'get_income_last_year',
                args: [posted],
            })
                .then(function (result) {

                    $('#net_profit_this_months').hide();
                    $('#net_profit_last_month').hide();
                    $('#net_profit_last_year').show();
                    $('#net_profit_this_year').hide();

                    var ctx = document.getElementById("canvas").getContext('2d');

                    // Define the data
                    var income = result.income; // Add data values to array
                    var expense = result.expense;
                    var profit = result.profit;

                    var labels = result.month; // Add labels to array
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
                                    backgroundColor: '#ffa500',
                                    borderColor: '#ffa500',

                                    borderWidth: 1, // Specify bar border width
                                    type: 'bar', // Set this data to a line chart
                                    fill: false
                                },
                                {
                                    label: 'Profit/Loss', // Name the series
                                    data: profit, // Specify the data values array
                                    backgroundColor: '#0bd465',
                                    borderColor: '#0bd465',

                                    borderWidth: 1, // Specify bar border width
                                    type: 'line', // Set this data to a line chart
                                    fill: false
                                }
                            ]
                        },
                        options: {
                            responsive: true, // Instruct chart js to respond nicely.
                            maintainAspectRatio: false, // Add to prevent default behaviour of full-width/height
                        }
                    });

                })
        },

        onclick_income_this_year: function (f) {
            //ev.preventDefault();
            var selected = $('.btn.btn-tool.income');
            var data = $(selected[0]).data();
            var posted = false;
            if ($('#toggle-two')[0].checked == true) {
                posted = "posted"
            }


            rpc.query({
                model: 'account.move',
                method: 'get_income_expense',
                args: [f],

            })
                .then(function (result) {


                    $('#net_profit_this_months').hide();
                    $('#net_profit_last_month').hide();
                    $('#net_profit_last_year').hide();
                    $('#net_profit_this_year').show();

                    var ctx = document.getElementById("canvas").getContext('2d');

                    // Define the data
                    var income = result.income; // Add data values to array
                    var expense = result.expense;
                    var profit = result.profit;

                    var labels = result.month; // Add labels to array


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
                                    backgroundColor: '#ffa500',
                                    borderColor: '#ffa500',

                                    borderWidth: 1, // Specify bar border width
                                    type: 'bar', // Set this data to a line chart
                                    fill: false
                                },
                                {
                                    label: 'Profit/Loss', // Name the series
                                    data: profit, // Specify the data values array
                                    backgroundColor: '#0bd465',
                                    borderColor: '#0bd465',

                                    borderWidth: 1, // Specify bar border width
                                    type: 'line', // Set this data to a line chart
                                    fill: false
                                }
                            ]
                        },
                        options: {
                            responsive: true, // Instruct chart js to respond nicely.
                            maintainAspectRatio: false, // Add to prevent default behaviour of full-width/height
                        }
                    });

                })
        },

        onclick_income_this_month: function (ev) {
            ev.preventDefault();
            var selected = $('.btn.btn-tool.income');
            var data = $(selected[0]).data();
            var posted = false;
            if ($('#toggle-two')[0].checked == true) {
                posted = "posted"
            }
            rpc.query({
                model: 'account.move',
                method: 'get_income_this_month',
                args: "posted",

            })
                .then(function (result) {


                    var ctx = document.getElementById("canvas").getContext('2d');

                    // Define the data
                    var income = result.income; // Add data values to array
                    var expense = result.expense;
                    var profit = result.profit;

                    var labels = result.date; // Add labels to array
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
                                    backgroundColor: '#ffa500',
                                    borderColor: '#ffa500',

                                    borderWidth: 1, // Specify bar border width
                                    type: 'bar', // Set this data to a line chart
                                    fill: false
                                },
                                {
                                    label: 'Profit/Loss', // Name the series
                                    data: profit, // Specify the data values array
                                    backgroundColor: '#0bd465',
                                    borderColor: '#0bd465',

                                    borderWidth: 1, // Specify bar border width
                                    type: 'line', // Set this data to a line chart
                                    fill: false
                                }
                            ]
                        },
                        options: {
                            responsive: true, // Instruct chart js to respond nicely.
                            maintainAspectRatio: false, // Add to prevent default behaviour of full-width/height
                        }
                    });

                })
        },

        renderElement: function (ev) {
            var self = this;
            $.when(this._super())
                .then(function (ev) {


                    $('#toggle-two').bootstrapToggle({
                        on: 'View All Entries',
                        off: 'View Posted Entries'
                    });


                    var posted = false;
                    if ($('#toggle-two')[0].checked == true) {
                        posted = "posted"
                    }


                    rpc.query({
                        model: "account.move",
                        method: "get_currency",
                    })
                        .then(function (result) {
                            currency = result;

                        })


                    rpc.query({
                        model: "account.move",
                        method: "get_income_expense",
                        args: ["income_this_year"],
                    })
                        .then(function (result) {

                            var ctx = document.getElementById("canvas").getContext('2d');

                            // Define the data
                            var income = result.income; // Add data values to array
                            var expense = result.expense;
                            var profit = result.profit;

                            var labels = result.month; // Add labels to array
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
                                            backgroundColor: '#ffa500',
                                            borderColor: '#ffa500',

                                            borderWidth: 1, // Specify bar border width
                                            type: 'bar', // Set this data to a line chart
                                            fill: false
                                        },
                                        {
                                            label: 'Profit/Loss', // Name the series
                                            data: profit, // Specify the data values array
                                            backgroundColor: '#0bd465',
                                            borderColor: '#0bd465',

                                            borderWidth: 1, // Specify bar border width
                                            type: 'line', // Set this data to a line chart
                                            fill: false
                                        }
                                    ]
                                },
                                options: {
                                    responsive: true, // Instruct chart js to respond nicely.
                                    maintainAspectRatio: false, // Add to prevent default behaviour of full-width/height
                                }
                            });

                        })

                    var arg = 'last_month'
                    rpc.query({
                        model: 'account.move',
                        method: 'get_investment_summary_pie',
                    })
                        .then(function (result) {
                            var total_amount = result.total_amount
                            total_amount = self.format_currency(currency, total_amount);
                            $('#total_inv_amount').append('<span>' + total_amount + '</span>')
                            $(document).ready(function () {
                                var options = {
                                    legend: false,
                                    responsive: true,
                                    legend: {
                                        position: 'bottom'
                                    }
                                };
                                if (window.donuts != undefined)
                                    window.donuts.destroy();
                                window.donuts = new Chart($("#horizontalbarChart"), {
                                    type: 'pie',
                                    tooltipFillColor: "rgba(51, 51, 51, 0.55)",
                                    data: {
                                        labels: result.label,
                                        datasets: [{
                                            data: result.amount,
                                            backgroundColor: [
                                                '#003f5c', '#7a5195', '#ef5675', '#ffa600', '#9c66cf',
                                                '#bc66cf ', '#b75fcc', ' #cb5fbf ', ' #cc5f7f ', ' #cc6260',
                                                '#cc815f', '#cca15f ', '#ccc25f', '#b9cf66', '#99cf66',
                                                ' #75cb5f ', '#60cc6c', '#804D8000', '#80B33300', '#80CC80CC', '#f2552c', '#00cccc',
                                                '#1f2e2e', '#993333', '#00cca3', '#1a1a00', '#3399ff',
                                                '#8066664D', '#80991AFF', '#808E666FF', '#804DB3FF', '#801AB399',
                                                '#80E666B3', '#8033991A', '#80CC9999', '#80B3B31A', '#8000E680',
                                                '#804D8066', '#80809980', '#80E6FF80', '#801AFF33', '#80999933',
                                                '#80FF3380', '#80CCCC00', '#8066E64D', '#804D80CC', '#809900B3',
                                                '#80E64D66', '#804DB380', '#80FF4D4D', '#8099E6E6', '#806666FF'
                                            ],
                                            hoverBackgroundColor: [
                                                '#003f5c', '#7a5195', '#ef5675', '#ffa600', '#9c66cf',
                                                '#bc66cf ', '#b75fcc', ' #cb5fbf ', ' #cc5f7f ', ' #cc6260',
                                                '#cc815f', '#cca15f ', '#ccc25f', '#b9cf66', '#99cf66',
                                                ' #75cb5f ', '#60cc6c', '#804D8000', '#80B33300', '#80CC80CC', '#f2552c', '#00cccc',
                                                '#1f2e2e', '#993333', '#00cca3', '#1a1a00', '#3399ff',
                                                '#8066664D', '#80991AFF', '#808E666FF', '#804DB3FF', '#801AB399',
                                                '#80E666B3', '#8033991A', '#80CC9999', '#80B3B31A', '#8000E680',
                                                '#804D8066', '#80809980', '#80E6FF80', '#801AFF33', '#80999933',
                                                '#80FF3380', '#80CCCC00', '#8066E64D', '#804D80CC', '#809900B3',
                                                '#80E64D66', '#804DB380', '#80FF4D4D', '#8099E6E6', '#806666FF'
                                            ]
                                        }]
                                    },
                                    options: {
                                        responsive: false
                                    }
                                });
                            });
                          })
                    rpc.query({
                        model: "account.move",
                        method: "get_bank_balance",
                    }).then(function (result) {
                            var due_count = 0;
                            var amount;
                            var total_amount = 0.00;
                            _.forEach(result, function (x) {
                                $('#bank_balance_list').show();
                                due_count++;
                                amount = self.format_currency(currency, x.amount);
                                total_amount += x.amount
                                $('#bank_balance_list').append('<li><div>' + x.percentage + '</div>' + '<div>' + amount + '</div>' + '</li>');
                            });
                            total_amount = self.format_currency(currency, total_amount);
                            $('#total_bank_balance').append('<span>' + total_amount + '</span>')
                        })

                   rpc.query({
                        model: "account.move",
                        method: "get_share_pl_summary",
                    }).then(function (result) {
                            var due_count = 0;
                            var amount;
                            var total_amount = 0.00;
                            _.forEach(result, function (x) {
                                $('#share_pl_list').show();
                                due_count++;
                                amount = self.format_currency(currency, x.amount);
                                total_amount += x.amount
                                $('#share_pl_list').append('<li><div>' + x.particulars + '</div>' + '<div>' + amount + '</div>' + '</li>');
                            });
                            var f_total_amount = self.format_currency(currency, total_amount);
                            if (total_amount>0.00){
                                $('#total_share_pl').append('<span style= "color:#008000;">' + f_total_amount + '</span>')
                            } else if(total_amount<0.00){
                                $('#total_share_pl').append('<span style= "color:#FF0000;">' + f_total_amount + '</span>')
                            } else {
                                 $('#total_share_pl').append('<span style= "color:#808080;">' + f_total_amount + '</span>')
                            }
                        })

                    rpc.query({
                        model: "account.move",
                        method: "get_fixed_deposit"
                    }).then(function (result) {
                            var due_count = 0;
                            var amount;
                            var total_amount = 0.00;
                            _.forEach(result, function (x) {
                                $('#fixed_deposit_list').show();
                                due_count++;
                                if (x.amount != 0.00) {
                                  amount = self.format_currency(currency, x.amount);
                                  total_amount += x.amount
                                  $('#fixed_deposit_list').append('<li><div>' + x.percentage + '</div>' + '<div>' + amount + '</div>' + '</li>');
                                }
                            });
                            total_amount = self.format_currency(currency, total_amount);
                            $('#totalfixeddeposit').append('<span>' + total_amount + '</span>')
                        })

                    rpc.query({
                        model: "account.move",
                        method: "get_salary_list"
                    }).then(function (result) {
                            var due_count = 0;
                            var amount;
                            var total_amount = 0.00;
                            _.forEach(result, function (x) {
                                $('#salary_list').show();
                                due_count++;
                                if (x.amount != 0.00) {
                                  amount = self.format_currency(currency, x.amount);
                                  total_amount += x.amount
                                  $('#salary_list').append('<li><div>' + x.particulars + '</div>' + '<div>' + amount + '</div>' + '</li>');
                                }
                            });
                            total_amount = self.format_currency(currency, total_amount);
                            $('#totalsalary').append('<span>' + total_amount + '</span>')
                        })

                    rpc.query({
                        model: "account.move",
                        method: "get_accounts_profit"
                    })
                        .then(function (result) {
                            var net_profit_this_year = result[0].profit;
                            var net_profit_this_months = result[1].profit;
                            var incomes_this_year = result[0].income;
                            var income_this_month = result[1].income;
                            var expenses_this_year = result[0].expense;
                            var expenses_this_month = result[1].expense;
                            var count_this_year = result[0].count;
                            var count_this_month = result[1].count;


                            net_profit_this_year = self.format_currency(currency, net_profit_this_year);
                            net_profit_this_months = self.format_currency(currency, net_profit_this_months);
                            incomes_this_year = self.format_currency(currency, incomes_this_year);
                            income_this_month = self.format_currency(currency, income_this_month);
                            expenses_this_year = self.format_currency(currency, expenses_this_year);
                            expenses_this_month = self.format_currency(currency, expenses_this_month);

                            $('#net_profit_current_year').append('<span>' + net_profit_this_year + '</span> <div class="title">This Year</div>')
                            $('#net_profit_current_months').append('<span>' + net_profit_this_months + '</span> <div class="title">This Month</div>')
                            $('#total_incomes_this_year').append('<span>' + incomes_this_year + '</span><div class="title">This Year</div>')
                            $('#total_incomes_').append('<span>' + income_this_month + '</span><div class="title">This month</div>')
                            $('#total_expense_this_year').append('<span >' + expenses_this_year + '</span><div class="title">This Year</div>')
                            $('#total_expenses_').append('<span>' + expenses_this_month + '</span><div class="title">This month</div>')
                            $('#count_this_year').append('<span>' + count_this_year + '</span><div class="title">This Year</div>')
                            $('#count_this_month').append('<span>' + count_this_month + '</span><div class="title">This month</div>')
                        })
                });
        },

        format_currency: function(currency, amount){
             if (typeof(amount) != 'number'){
                amount = parseFloat(amount);
             }
             var formatted_value = (parseInt(amount)).toLocaleString(currency.language, {minimumFractionDigits: 2})
             if (currency.position === "after") {
                return formatted_value += ' ' + currency.symbol;
             } else {
                return currency.symbol + ' ' + formatted_value;
             }
        },

        willStart: function () {
            var self = this;
            self.drpdn_show = false;
            return Promise.all([ajax.loadLibs(this), this._super()]);
        },
    });
    core.action_registry.add('invoice_dashboard', ActionMenu);

});