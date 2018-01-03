/*
 * Partition 1, Item 1:
 * Simple Equation Solver
 *
 * "Apps that makes work easier"
 *
 * For SDC 2018
 *
 * Contact: cisoftwaremaster@gmail.com
 *
 */

// this is our callback function for the "onload" event
window.onload = function() {
    // these variables will store references (pointers) to important element nodes
    var ses_input = undefined;
    var ses_output = undefined;

    // this will be used by ses_print_line later
    var output_template = "<div class='row'><p>~body</p></div>";

    // function declarations
    function ses_get_references() {
        if (document.getElementById("se-input")) ses_input = document.getElementById("se-input");
        if (document.getElementById("se-output")) ses_output = document.getElementById("se-output");

        return (ses_input != undefined && ses_output != undefined);
    }

    function ses_clear_output() {
        if (ses_output != undefined) {
            ses_output.innerHTML = '';
        }
    }

    function ses_print_line(line, with_newline=true) {
        if (ses_output != undefined) {
            ses_output.innerHTML += output_template.replace("~body", line);
        }
    }

    function ses_get_input() {
        if (ses_input != undefined) {
            return ses_input.value;
        }

        return undefined;
    }

    // create a new term object
    function ses_make_term(coefficient, variable='', degree=0, is_positive=true) {
        return {
            coefficient: coefficient,
            variable: variable,
            degree: degree,
            is_positive: is_positive,

            to_string: function() {
                return `C: ${coefficient} V: ${variable} D: ${degree}, P: ${is_positive}`;
            }
        };
    }

    // find the degree (highest exponent) of an equation
    function ses_get_degree(terms) {
        var highest = 0;

        for (var term of terms) {
            if (term.degree > highest) {
                highest = term.degree;
            }
        }

        return highest;
    }

    function ses_get_name_by_degree(degree) {
        switch (degree) {
            case 0: return "Constant"; break;
            case 1: return "Linear"; break;
            case 2: return "Quadratic"; break;
            case 3: return "Cubic"; break;
            case 4: return "Quartic"; break;
            case 5: return "Quintic"; break;
            case 6: return "Sextic"; break;
            case 7: return "Septic"; break;
            case 8: return "Octic"; break;
            case 9: return "Nonic"; break;
            case 10: return "Dedic"; break;
            default: return "Unknown"; break;
        }
    }

    // this function combines the coefficient and is_positive properties
    function ses_prepare(terms) {
        var new_terms = new Array();

        for (var term of terms) {
            new_terms.push({
                coefficient: (term.is_positive ? term.coefficient : -term.coefficient),
                variable: term.variable,
                degree: term.degree
            });
        }

        return new_terms;
    }

    // this function will combine terms by their exponent
    function ses_combine_by_degree(terms) {
        var new_terms = new Array();

        // prepare for combination
        terms = ses_prepare(terms);

        for (var term of terms) {
            var matched = false;

            // see if matches anything in the new_terms array
            for (var x in new_terms) {
                if ((term.degree == new_terms[x].degree) &&
                    (term.variable == new_terms[x].variable)) {
                    new_terms[x].coefficient += term.coefficient
                    matched = true;
                    break;
                }
            }

            // otherwise, insert it
            if (!matched) {
                new_terms.push(term);
            }
        }

        return new_terms;
    }

    // invert the coefficients inside "terms"
    function ses_invert_coefficients(terms, exclude='x') {
        var new_terms = new Array();

        for (var x = 0, l = terms.length; x < l; ++x) {
            var term = terms[x];

            if (term.variable != exclude) {
                term.coefficient *= -1;
                new_terms.push(term);
            }
        }

        return new_terms;
    }

    // calculate the sum of coefficients of "terms"
    function ses_sum_of_terms(terms, exclude='x') {
        var sum = 0;

        for (term of terms) {
            if (term.variable != exclude) {
                sum += term.coefficient;
            }
        }

        return sum;
    }

    // get a term with an exponent that matches this function's parameter
    function ses_get_term(terms, degree) {
        for (var x = 0, l = terms.length; x < l; ++x) {
            if (terms[x].degree == degree) {
                return terms[x];
            }
        }
        return NaN;
    }

    // divide the terms' coefficients using a given divisor, but exclude "x"
    function ses_divide_coefficients(terms, divisor, x) {
        var new_terms = new Array();

        for (var term of terms) {
            if (term.variable != x) {
                term.coefficient /= divisor;
                new_terms.push(term);
            }
        }

        return new_terms;
    }

    // combine terms into a readable format
    function ses_render_equation(terms) {
        var equation = "";

        for (var x = 0, l = terms.length; x < l; ++x) {
            var term = terms[x];

            // assign operations according to their sign
            if (x > 0) {
                if (term.coefficient < 0) {
                    equation += " - ";
                } else {
                    equation += " + ";
                }
            }

            equation += `${(Math.abs(term.coefficient) == 1 && term.variable != '' ? '' : Math.abs(term.coefficient))}${term.variable}`
                     +  (term.degree != 0 && term.degree != 1 ? `^${term.degree}` : "");
        }

        return equation;
    }

    // check if "terms" are made entirely of constants
    function ses_terms_are_constants(terms, exclude='x') {
        for (var x = 0, l = terms.length; x < l; ++x) {
            if (terms[x].variable != '' && terms[x].variable != exclude) {
                return false;
            }
        }
        return true;
    }

    // try to get references
    ses_get_references();

    // handle the se-btn-solve click event
    if (document.getElementById("se-btn-solve")) {
        document.getElementById("se-btn-solve").onclick = function() {
            var equation = ses_get_input();

            // check if we successfully got the input equation
            if (equation != undefined) {
                // prepare our equation for extraction
                equation = equation.replace(/ /g, "");

                // handle the equal sign behaviour
                var tmp_equation = equation.split("=");


                if (tmp_equation.length == 2) {
                    equation = tmp_equation[0];
                }

                // to make sign extraction easier
                equation = equation.replace(/\+/g, "@");
                equation = equation.replace(/\-/g, "@-");

                if (tmp_equation.length == 2) {
                    tmp_equation = tmp_equation[1];

                    // exclude the first term
                    var ifs = tmp_equation.search(/(\-|\+)/);

                    var tmp_first = tmp_equation.slice(0, ifs);
                    tmp_equation = tmp_equation.slice(ifs, tmp_equation.length);

                    // "reverse the polarity of the first term-pole"
                    if (tmp_first.charAt(0) == '-') {
                        // make it positive
                        tmp_first = tmp_first.slice(1, tmp_first.length);
                    } else {
                        tmp_first = '-' + tmp_first;
                    }

                    // reverse its terms' sign
                    tmp_equation = tmp_equation.replace(/\-/g, "@");
                    tmp_equation = tmp_equation.replace(/\+/g, "@-");

                    tmp_equation = tmp_first + tmp_equation;

                    // merge
                    equation = `${equation}@${tmp_equation}`;
                }

                // we will store our terms here
                var terms = new Array();

                // let's try to extract our equation's terms
                for (var term of equation.split('@')) {
                    var parts = term.split('^');

                    // extract term properties
                    var is_positive = (parts[0].replace(/[^-]/g, '').length == 0);
                    var coefficient = parseFloat(parts[0].replace(/\D/g, ''));
                    var variable = parts[0].replace(/[^A-z]/g, '');

                    if (parts.length == 2) {
                        var degree = parseFloat(parts[1].replace(/\D/g, ''));
                    } else {
                        var degree = (variable.length > 0 ? 1 : 0);
                    }

                    // fail-safe for NaN coefficients
                    if (!coefficient && variable.length > 0) {
                        coefficient = 1;
                    }

                    // only proceed if our extraction operation is successful
                    if (coefficient) {
                        var n_term = ses_make_term(coefficient, variable, degree, is_positive);
                        terms.push(n_term);
                    }
                }

                // get the degree of our equation
                var degree = ses_get_degree(terms);

                // print equation type
                ses_print_line(`[SES function type detection: ${ses_get_name_by_degree(degree)} equation.]`);

                // clean up
                var combined = ses_combine_by_degree(terms);

                // try to find the first variable
                var main_variable = -1;
                // the main variable's index in the Array
                var varindex = 0;

                for (var x = 0, l = combined.length; x < l; ++x) {
                    if (combined[x].variable != '') {
                        main_variable = combined[x].variable;
                        varindex = x;
                        break;
                    }
                }

                if (main_variable == -1) {
                    ses_print_line("[Error: SES cannot solve this equation, (no variables found!)]");
                    return;
                }

                ses_print_line(`[Note: SES is solving for ${main_variable}]`);

                // for linear equations
                if (degree == 1) {
                    // show solving instructions
                    ses_print_line(`1. Move all terms to the left<Br /> ${ses_render_equation(terms)}`);
                    ses_print_line(`2. Combine like terms<br />${ses_render_equation(combined)}`);
                    ses_print_line(`3. Move other terms back to the right, then divide everything by ${combined[varindex].coefficient}`);

                    // move the other terms back to the right side
                    var final_terms = ses_invert_coefficients(combined, main_variable);

                    if (combined[varindex].coefficient == 1) {
                        // if the main variable's coefficient is one, just print the equation
                        ses_print_line(`4. Done!<br />${main_variable} = ${ses_render_equation(final_terms)}`);
                    } else {
                        // divide final_terms by [main_variable]
                        if (ses_terms_are_constants(combined, main_variable)) {
                            var x = ses_sum_of_terms(final_terms, main_variable) / combined[varindex].coefficient;
                            ses_print_line(`4. Done!<br />${main_variable} = ${x}`);
                        } else {
                            final_terms = ses_divide_coefficients(final_terms, combined[varindex].coefficient, main_variable);
                            ses_print_line(`4. Done!<br />${main_variable} = ${ses_render_equation(final_terms)}`);
                        }
                    }
                }

                // for quadratic equations
                else if (degree == 2) {
                    // get the coefficients to solve the equation
                    var param_a = ses_get_term(combined, 2).coefficient;
                    var param_b = ses_get_term(combined, 1).coefficient;
                    var param_c = ses_get_term(combined, 0).coefficient;

                    if (!param_a) param_a = 0;
                    if (!param_b) param_b = 0;
                    if (!param_c) param_c = 0;

                    // solve it using the quadratic formula
                    // b^2 - 4ac
                    var mid = ((param_b*param_b) - 4*param_a*param_c);

                    // take the square root of "mid"
                    if (mid < 0) {
                        mid = Math.sqrt(Math.abs(mid));
                        ses_print_line("[Warning: the square root is invalid, we will use the absolute value instead...]");
                    } else {
                        mid = Math.sqrt(mid);
                    }

                    // solve the roots
                    var roots = [(-param_b + mid)/2*param_a, (-param_b - mid)/2*param_a];

                    ses_print_line(`1. a = ${param_a}, b = ${param_b}. c = ${param_c}`);
                    ses_print_line("2. Solve using the quadratic formula, (-b +- sqrt[b^2 - 4ac])/2a");
                    ses_print_line(`3. sqrt(b^2 - 4ac) = ${mid}`);
                    ses_print_line(`4. Done!<br />${main_variable} = ${roots[0]}, ${main_variable} = ${roots[1]}`);
                }

                // for cubic equations
                // this formula was obtained from https://math.vanderbilt.edu/schectex/courses/cubic/
                else if (degree == 3) {
                    var param_a = ses_get_term(combined, 3).coefficient;
                    var param_b = ses_get_term(combined, 2).coefficient;
                    var param_c = ses_get_term(combined, 1).coefficient;
                    var param_d = ses_get_term(combined, 0).coefficient;

                    if (!param_a) param_a = 0;
                    if (!param_b) param_b = 0;
                    if (!param_c) param_c = 0;
                    if (!param_d) param_d = 0;

                    ses_print_line(`1. a = ${param_a}, b = ${param_b}, c = ${param_c}, d=${param_d}`);
                    ses_print_line("2. SES uses this <a href='https://math.vanderbilt.edu/schectex/courses/cubic/'>formula</a>.");

                    var param_p = (-param_b/3 * param_a);
                    var param_q = Math.pow(param_p, 3) + (param_b*param_c - 3*param_a*param_d)/6 * Math.pow(param_a, 2);
                    var param_r = param_c / 3 * param_a;

                    ses_print_line(`3. p = ${param_p}`);
                    ses_print_line(`4. q = ${param_q}`);
                    ses_print_line(`5. r = ${param_r}`);

                    var mid = Math.sqrt(Math.pow(param_q, 2) + Math.pow(param_r - Math.pow(param_p, 2), 3));

                    ses_print_line(`6. (r-p^2)^3]^1/2 = ${mid}, <= will be referred to as m`);

                    var x = Math.pow(param_q + mid, 1/3) + Math.pow(param_q - mid, 1/3) + param_p;

                    ses_print_line("7. (q + m)^1/3 + (q - m)^1/3 + p");

                    if (x) {
                        ses_print_line(`8. Done<br />${main_variable} is approximately ${x}`);
                    } else {
                        ses_print_line(`[Error: SES cannot solve this equation, as ${main_variable} becomes invalid]`);
                    }
                }
                else {
                    ses_print_line("[Error: SES cannot solve this type of equations yet!]");
                }

                // final spacer
                ses_print_line("<---------------- End of SES output --------------->");
            }
        };
    }

    // handle clear output button
    if (document.getElementById("se-btn-clear-output")) {
        document.getElementById("se-btn-clear-output").onclick = ses_clear_output;
    }
};
