let quotes = [
    "A program that has not been tested does not work.",
    "An organisation that treats its programmers as morons will soon have programmers that are willing and able to act like morons only.",
    "Anybody who comes to you and says he has a perfect language is either naïve or a salesman.",
    "C makes it easy to shoot yourself in the foot; C++ makes it harder, but when you do it blows your whole leg off.",
];

function quote(msg)
{
    return msg.reply(quotes[Math.floor(Math.random() * quotes.length)] + " - Bjarne Stroustrup.").catch(console.error);
}

module.exports = quote;
