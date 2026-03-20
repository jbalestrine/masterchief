with open('features/manager.py', 'r') as f:
    content = f.read()

# Fix the PowerShell exception lines
content = content.replace('                            self.app.logger.error(f"Failed to execute PowerShell script content: {e}")', '                self.app.logger.error(f"Failed to execute PowerShell script content: {e}")')
content = content.replace('                            raise', '                raise')

with open('features/manager.py', 'w') as f:
    f.write(content)

print('Fixed PowerShell exception indentation')