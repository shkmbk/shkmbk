odoo.define('InvestmentDashboard.InvestmentDashboard', function (require) {
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

        template: 'Investmentdashboard',

        events: {
            'click .investment_dashboard': 'onclick_dashboard',
            'click #prog_bar': 'onclick_prog_bar',
            'click #bank_balance': 'onclick_bank_balance',
            'click #bank_balance_hide': 'onclick_bank_balance_hide',
            'click #in_ex_hide': 'onclick_in_ex_hide',
            'change #toggle-two': 'onclick_toggle_two',
        },
        onclick_toggle_two: function (ev) {
        this.onclick_bank_balance(ev);
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
                        method: "get_investment_summary"
                    }).then(function (result) {
                            var due_count = 0;
                            var amount;
                            var total_amount = 0.00;
                            _.forEach(result, function (x) {
                                $('#investment_list').show();
                                due_count++;
                                amount = self.format_currency(currency, x.amount);
                                total_amount += x.amount
                                $('#investment_list').append('<li><div>' + x.percentage + '</div>' + '<div>' + amount + '</div>' + '</li>');
                            });
                            total_amount = self.format_currency(currency, total_amount);
                            $('#total_investment').append('<span>' + total_amount + '</span>')
                        })

                    rpc.query({
                        model: "account.move",
                        method: "get_fd_summary"
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
                        method: "get_investment_profit"
                    })
                        .then(function (result) {
                            var net_profit_this_year = result[0].profit;
                            var net_profit_this_months = result[1].profit;
                            var incomes_this_year = result[0].income;
                            var income_this_month = result[1].income;
                            var expenses_this_year = result[0].expense;
                            var expenses_this_month = result[1].expense;

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
                        })

                    rpc.query({
                        model: "account.move",
                        method: "get_investment_values"
                    })
                        .then(function (result) {
                            var investment_this_year = result[0].investment
                            var investment_this_month = result[1].investment

                            investment_this_year = self.format_currency(currency, investment_this_year);
                            investment_this_month = self.format_currency(currency, investment_this_month);

                            $('#investment_this_year').append('<span>' + investment_this_year + '</span><div class="title">This Year</div>')
                            $('#investment_this_month').append('<span>' + investment_this_month + '</span><div class="title">This month</div>')
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
                        method: "get_investment_pl_summary",
                    }).then(function (result) {
                            var due_count = 0;
                            var amount;
                            var total_amount = 0.00;
                            _.forEach(result, function (x) {
                                $('#pl_list').show();
                                due_count++;
                                amount = self.format_currency(currency, x.amount);
                                total_amount += x.amount
                                $('#pl_list').append('<li><div>' + x.percentage + '</div>' + '<div>' + amount + '</div>' + '</li>');
                            });
                            var f_total_amount = self.format_currency(currency, total_amount);
                            if (total_amount>0.00){
                                $('#total_pl').append('<span style= "color:#008000;">' + f_total_amount + '</span>')
                            } else if(total_amount<0.00){
                                $('#total_pl').append('<span style= "color:#FF0000;">' + f_total_amount + '</span>')
                            } else {
                                 $('#total_pl').append('<span style= "color:#808080;">' + f_total_amount + '</span>')
                            }
                        })

                   rpc.query({
                        model: "account.move",
                        method: "get_securities_summary",
                    }).then(function (result) {
                            var due_count = 0;
                            var amount;
                            var total_amount = 0.00;
                            _.forEach(result, function (x) {
                                $('#securities_list').show();
                                due_count++;
                                amount = self.format_currency(currency, x.amount);
                                if (Math.abs(x.amount) > 0.05) {
                                    total_amount += x.amount
                                    $('#securities_list').append('<li><div>' + x.percentage + '</div>' + '<div>' + amount + '</div>' + '</li>');
                                }
                            });
                            total_amount = self.format_currency(currency, total_amount);
                            $('#total_securities').append('<span>' + total_amount + '</span>')
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

                    rpc.query({
                        model: "account.move",
                        method: "get_inv_net_summary",
                    })
                        .then(function (result) {

                            var ctx = document.getElementById("canvas").getContext('2d');
                            var ctx1 = document.getElementById("canvas1").getContext('2d');

                            // Define the data
                            var fd_free = result.fd_free; // Add data values to array
                            var fd_en = result.fd_en; // Add data values to array
                            var share = result.share;
                            var share_invested = result.share_invested;
                            var bond = result.bond;

                            var labels = result.particulars; // Add labels to array
                            // End Defining data

                            // End Defining data
                            if (window.myCharts != undefined)
                                window.myCharts.destroy();
                            window.myCharts = new Chart(ctx, {
                                //var myChart = new Chart(ctx, {
                                type: 'line',
                                data: {
                                    labels: labels,
                                    datasets: [{
                                        label: 'FD Free', // Name the series
                                        data: fd_free, // Specify the data values array
                                        backgroundColor: '#66aecf',
                                        borderColor: '#66aecf',

                                        borderWidth: 3, // Specify bar border width
                                        type: 'line', // Set this data to a line chart
                                        fill: false
                                    },
                                        {
                                            label: 'FD Encumbered', // Name the series
                                            data: fd_en, // Specify the data values array
                                            backgroundColor: '#800000',
                                            borderColor: '#800000',

                                            borderWidth: 3, // Specify bar border width
                                            type: 'line', // Set this data to a line chart
                                            fill: false
                                        },
                                        {
                                            label: 'Stock', // Name the series
                                            data: share, // Specify the data values array
                                            backgroundColor: '#ffa500',
                                            borderColor: '#ffa500',

                                            borderWidth: 3, // Specify bar border width
                                            type: 'line', // Set this data to a line chart
                                            fill: false
                                        },
                                        {
                                            label: 'Debentures', // Name the series
                                            data: bond, // Specify the data values array
                                            backgroundColor: '#0bd465',
                                            borderColor: '#0bd465',

                                            borderWidth: 3, // Specify bar border width
                                            type: 'line', // Set this data to a line chart
                                            fill: false
                                        }
                                    ]
                                },
                                options: {
                                    responsive: true, // Instruct chart js to respond nicely.
                                    maintainAspectRatio: false, // Add to prevent default behaviour of full-width/height
                                },
                                    scales: {
                                            xAxes: [{
                                                type: 'time',
                                                display: true,
                                                scaleLabel: {
                                                    display: true,
                                                    labelString: 'Date'
                                                },
                                                ticks: {
                                                    major: {
                                                        fontStyle: 'bold',
                                                        fontColor: '#FF0000'
                                                    }
                                                }
                                            }],
                                            yAxes: [{
                                                display: true,
                                                scaleLabel: {
                                                    display: true,
                                                    labelString: 'value'
                                                }
                                            }]
                                        }
                            });

                            if (window.marketCharts != undefined)
                                window.marketCharts.destroy();
                            window.marketCharts = new Chart(ctx1, {
                                //var myChart = new Chart(ctx, {
                                type: 'line',
                                data: {
                                    labels: labels,
                                    datasets: [{
                                        label: 'Invested Value', // Name the series
                                        data: share_invested, // Specify the data values array
                                        backgroundColor: '#66aecf',
                                        borderColor: '#66aecf',

                                        borderWidth: 3, // Specify bar border width
                                        type: 'line', // Set this data to a line chart
                                        fill: false
                                    },
                                        {
                                            label: 'Market Value', // Name the series
                                            data: share, // Specify the data values array
                                            backgroundColor: '#800000',
                                            borderColor: '#800000',

                                            borderWidth: 3, // Specify bar border width
                                            type: 'line', // Set this data to a line chart
                                            fill: false
                                        }
                                    ]
                                },
                                options: {
                                    responsive: true, // Instruct chart js to respond nicely.
                                    maintainAspectRatio: false, // Add to prevent default behaviour of full-width/height
                                },
                                    scales: {
                                            xAxes: [{
                                                type: 'time',
                                                display: true,
                                                scaleLabel: {
                                                    display: true,
                                                    labelString: 'Date'
                                                },
                                                ticks: {
                                                    major: {
                                                        fontStyle: 'bold',
                                                        fontColor: '#FF0000'
                                                    }
                                                }
                                            }],
                                            yAxes: [{
                                                display: true,
                                                scaleLabel: {
                                                    display: true,
                                                    labelString: 'value'
                                                }
                                            }]
                                        }
                            });


                        })


                });
        },

        format_currency: function(currency, amount){
             if (typeof(amount) != 'number'){
                amount = parseFloat(amount);
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
    core.action_registry.add('investment_dashboard', ActionMenu);

});