with open("src/app/dashboard/workers/[id]/page.tsx", "r") as f:
    content = f.read()

# Add new imports
content = content.replace("import { DollarSign, Clock, Activity, Key } from 'lucide-react';", "import { DollarSign, Clock, Activity, Key, CheckCircle2, Circle, FileText, Upload, Download, MessageCircle, Link as LinkIcon, Trash } from 'lucide-react';")

# We will just write a whole new file instead of complex patching.
