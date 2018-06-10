"""Author: Trinity Core Team 

MIT License

Copyright (c) 2018 Trinity

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE."""

from twisted.internet import reactor,protocol

class QuickClient(protocol.Protocol):
      def connectionMade(self):
          print(dir(self.transport.getPeer()))
          print("port:%s type:%s "%(self.transport.getPeer().port, self.transport.getPeer().type))
          print("connection to ",self.transport.getPeer().host)


class BasicClientFactory(protocol.ClientFactory):
     protocol = QuickClient
     def clientConnectionLost(self, connector, reason):
         print("connection lost ",reason.getErrorMessage())
         reactor.stop()
     def clientConnectionFailed(self, connector, reason):
         print("connection failed ",reason.getErrorMessage())
         reactor.stop()


reactor.connectTCP('www.baidu.com', 80, BasicClientFactory())
reactor.run()