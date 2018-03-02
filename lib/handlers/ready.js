function ready()
{
    console.log(`Logged in as ${dClient.user.username} (${dClient.user.id}), ready to serve ${dClient.guilds.size} guild${(dClient.guilds.size > 1) ? "s" : ""}.`);

    // load handlers
    for (const event in dClient.lib.handlers)
    {
        if (event === "ready") continue;
        dClient.on(event, dClient.lib.handlers[event]);
    }
}

module.exports = ready;
