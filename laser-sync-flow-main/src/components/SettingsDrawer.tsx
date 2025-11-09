import { X, LogOut, User, Wifi, CheckCircle, Calendar } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Separator } from "@/components/ui/separator";
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet";

interface SettingsDrawerProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export const SettingsDrawer = ({ open, onOpenChange }: SettingsDrawerProps) => {
  const operatorName = "John Anderson";
  const jobsCompleted = 247;
  const scheduledJobs = [
    { time: "08:00 AM", project: "Steel Brackets - Series A" },
    { time: "10:30 AM", project: "Aluminum Panels - QTY 50" },
    { time: "02:00 PM", project: "Custom Fabrication - Client XYZ" },
  ];

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent side="right" className="w-80 bg-card">
        <SheetHeader>
          <SheetTitle className="text-foreground">Settings</SheetTitle>
        </SheetHeader>

        <div className="mt-6 space-y-6">
          {/* Operator Profile */}
          <div className="flex items-center gap-4">
            <Avatar className="h-16 w-16 border-2 border-primary">
              <AvatarImage src="" alt={operatorName} />
              <AvatarFallback className="bg-primary text-primary-foreground text-lg font-bold">
                {operatorName.split(' ').map(n => n[0]).join('')}
              </AvatarFallback>
            </Avatar>
            <div>
              <p className="font-bold text-foreground">{operatorName}</p>
              <p className="text-sm text-muted-foreground">Operator</p>
            </div>
          </div>

          <Separator className="bg-border" />

          {/* Connection Status */}
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-sm">
              <Wifi className="h-4 w-4 text-status-complete" />
              <span className="text-foreground">Connected to PC</span>
            </div>
            <p className="text-xs text-muted-foreground pl-6">
              LASER-PC-001
            </p>
          </div>

          <Separator className="bg-border" />

          {/* Jobs Completed */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <CheckCircle className="h-5 w-5 text-status-complete" />
              <span className="text-sm text-foreground">Jobs Completed</span>
            </div>
            <span className="text-2xl font-bold text-primary">{jobsCompleted}</span>
          </div>

          <Separator className="bg-border" />

          {/* Scheduled Jobs Today */}
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <Calendar className="h-5 w-5 text-accent" />
              <span className="text-sm font-semibold text-foreground">Today's Schedule</span>
            </div>
            <div className="space-y-2">
              {scheduledJobs.map((job, index) => (
                <div
                  key={index}
                  className="rounded-lg bg-secondary p-3 transition-fast hover:bg-secondary/80"
                >
                  <p className="text-xs font-semibold text-primary">{job.time}</p>
                  <p className="text-sm text-foreground">{job.project}</p>
                </div>
              ))}
            </div>
          </div>

          <Separator className="bg-border" />

          {/* Logout Button */}
          <Button
            variant="destructive"
            className="w-full"
            onClick={() => {
              // Handle logout
              onOpenChange(false);
            }}
          >
            <LogOut className="mr-2 h-4 w-4" />
            Logout
          </Button>
        </div>
      </SheetContent>
    </Sheet>
  );
};
