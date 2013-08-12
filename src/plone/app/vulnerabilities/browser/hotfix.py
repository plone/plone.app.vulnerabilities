from Products.Five.browser import BrowserView

class HotfixView(BrowserView):


	def get_vulnerabilities(self):
		return self.context.getFolderContents()
