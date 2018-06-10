var Dispute = artifacts.require('Dispute')


contract('Dispute', (accounts) => {
    var address = accounts[0]
    var address1 = accounts[1]

    it('ecrecover result matches address', async function() {
        var instance = await Dispute.deployed()
        var msg = 'hello'
        var h = web3.sha3(msg)
        //console.log(h)
        var sig = web3.eth.sign(address, h).slice(2)
        var r = `0x${sig.slice(0, 64)}`
        var s = `0x${sig.slice(64, 128)}`
        var v = web3.toDecimal(sig.slice(128, 130)) + 27

        var result = await instance.testRecovery.call(h, v, r, s)
        var result2 = await instance.validate.call(h, v, r, s)
        //console.log(result)
        //console.log(result2)
    })

    it('votes', async function() {
        var instance = await Dispute.deployed()
        var msg = ['1','2']
        var h = [web3.sha3(msg[0]),web3.sha3(msg[1])]
        var sig = [web3.eth.sign(address, h[0]).slice(2), web3.eth.sign(address1, h[1]).slice(2)]
        var r = [`0x${sig[0].slice(0, 64)}`, `0x${sig[1].slice(0, 64)}`]
        var s = [`0x${sig[0].slice(64, 128)}`, `0x${sig[1].slice(64, 128)}`]
        var v = [web3.toDecimal(sig[0].slice(128, 130)) + 27, web3.toDecimal(sig[1].slice(128, 130)) + 27 ]
        console.log(h)
        console.log(v)
        console.log(r)
        console.log(s)
        await instance.setArbitratorsAndVotes.call(h, v, r, s, "test")
        //console.log(result)
        //let vote2 = await instance.votes.call(1);
        //console.log(vote2)
        //let arbitrator1 = await instance.arbitrators.call(0);
        //console.log(arbitrator1)
        //let arbitrator2 = await instance.arbitrators.call(1);
        //console.log(arbitrator2)
        //var result2 = await instance.validate.call(h, v, r, s)
        //console.log(result)
        //console.log(result2)
    })
})