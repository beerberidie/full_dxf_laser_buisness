import { LucideIcon } from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface DashboardCardProps {
  title: string;
  description: string;
  icon: LucideIcon;
  count: number;
  onClick: () => void;
}

export const DashboardCard = ({
  title,
  description,
  icon: Icon,
  count,
  onClick,
}: DashboardCardProps) => {
  return (
    <Card
      className="cursor-pointer border-border bg-card shadow-elevation-2 transition-smooth hover:shadow-elevation-3 hover:scale-[1.02]"
      onClick={onClick}
    >
      <CardHeader className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="rounded-lg bg-primary/10 p-3">
            <Icon className="h-6 w-6 text-primary" />
          </div>
          <Badge variant="secondary" className="text-lg font-bold">
            {count}
          </Badge>
        </div>
        
        <div>
          <CardTitle className="text-xl text-foreground">{title}</CardTitle>
          <CardDescription className="mt-1 text-muted-foreground">
            {description}
          </CardDescription>
        </div>
      </CardHeader>
    </Card>
  );
};
