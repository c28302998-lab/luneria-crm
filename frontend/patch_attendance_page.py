with open("src/app/dashboard/attendance/page.tsx", "r") as f:
    content = f.read()

# Add Clock to lucide-react imports if not there
if "Clock" not in content.split("from 'lucide-react'")[0]:
    content = content.replace("CheckCircle2, Circle", "CheckCircle2, Circle, Clock")

# Update logic
old_logic = """                          >
                            {isPresent ? (
                              <CheckCircle2 className="w-8 h-8 text-green-500 mx-auto" />
                            ) : (
                              <Circle className="w-8 h-8 text-gray-300 mx-auto hover:text-gray-400" />
                            )}
                          </button>"""
new_logic = """                          >
                            {att?.status === 'PENDING' ? (
                              <Clock className="w-8 h-8 text-yellow-500 mx-auto animate-pulse" />
                            ) : isPresent ? (
                              <CheckCircle2 className="w-8 h-8 text-green-500 mx-auto" />
                            ) : (
                              <Circle className="w-8 h-8 text-gray-300 mx-auto hover:text-gray-400" />
                            )}
                          </button>"""
content = content.replace(old_logic, new_logic)

with open("src/app/dashboard/attendance/page.tsx", "w") as f:
    f.write(content)
