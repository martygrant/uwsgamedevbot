function factorial(number)
{
    if (number < 0)
        return -1;
    else if (number === 0)
        return 1;
    else
        return (number * factorial(number - 1));
}

function math(msg)
{
    if (!msg.args.length) return msg.reply("You need to enter a valid mathematical expression.").catch(console.error);

    if (msg.args.length === 3)
    {
        let operator = msg.args[1]
        , number1 = parseInt(msg.args[0])
        , number2 = parseInt(msg.args[2])
        , result;

        if (Number.isNaN(number1) || Number.isNaN(number2)) return msg.reply("Your numbers seem to be.. *not* numbers. Try again.").catch(console.error);

        if (operator === "+") result = number1 + number2;
        else if (operator === "-") result = number1 - number2;
        else if (operator === "*") result = number1 * number2;
        else if (operator === "/") result = number1 / number2;
        else if (operator === "^") result = Math.pow(number1, number2);
        else return msg.reply("You have entered an invalid operator. Pick either `+`, `-`, `*`, `/`, or `^`.").catch(console.error);

        return msg.channel.send(result, { code: "js" }).catch(console.error);
    }

    else
    {
        let expression = msg.args.join(" ").toLowerCase();

        let sqrtRegExp = /sqrt *\(?(\d+)\)?/
        , factorialRegExp = /! *?(\d+)/g;

        if (expression.includes("sqrt"))
        {
            let number = sqrtRegExp.exec(expression)[1];

            return msg.channel.send(Math.sqrt(number), { code: "js" }).catch(console.error);
        }

        else if (expression.startsWith("!"))
        {
            let number = factorialRegExp.exec(expression)[1];

            return msg.channel.send(factorial(number), { code: "js" }).catch(console.error);
        }
    }
}

module.exports = math;
