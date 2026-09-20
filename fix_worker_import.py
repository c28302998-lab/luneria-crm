with open('frontend/src/app/dashboard/workers/[id]/page.tsx', 'r') as f:
    content = f.read()

content = content.replace("} from 'UserMinus } from 'lucide-react';", ", UserMinus } from 'lucide-react';")

with open('frontend/src/app/dashboard/workers/[id]/page.tsx', 'w') as f:
    f.write(content)
