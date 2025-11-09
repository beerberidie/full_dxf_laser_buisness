import { ArrowLeft, Play, Pause, CheckCircle, Edit, Download, FileText } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Job } from "@/types/job";
import { cn } from "@/lib/utils";

interface JobDetailsViewProps {
  job: Job;
  onBack: () => void;
  onStart: () => void;
  onPause: () => void;
  onComplete: () => void;
  onEdit: () => void;
}

export const JobDetailsView = ({
  job,
  onBack,
  onStart,
  onPause,
  onComplete,
  onEdit,
}: JobDetailsViewProps) => {
  const getStatusColor = (status: Job["status"]) => {
    switch (status) {
      case "running":
        return "bg-status-running";
      case "paused":
        return "bg-status-paused";
      case "complete":
        return "bg-status-complete";
      default:
        return "bg-status-pending";
    }
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="sticky top-0 z-10 border-b border-border bg-card shadow-elevation-2">
        <div className="flex items-center gap-3 p-4">
          <Button variant="ghost" size="icon" onClick={onBack}>
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <h1 className="flex-1 text-lg font-bold text-foreground">{job.projectName}</h1>
          <Badge className={cn("text-white", getStatusColor(job.status))}>
            {job.status.toUpperCase()}
          </Badge>
        </div>
      </div>

      {/* Content */}
      <div className="space-y-4 p-4">
        {/* Main Info Card */}
        <Card className="border-border bg-card shadow-elevation-1">
          <CardHeader>
            <CardTitle className="text-foreground">Job Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Material Type</p>
                <p className="font-semibold text-foreground">{job.materialType}</p>
              </div>
              
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Thickness</p>
                <p className="font-semibold text-foreground">{job.thickness} mm</p>
              </div>
              
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Raw Plates</p>
                <p className="font-semibold text-foreground">{job.rawPlateCount}</p>
              </div>
              
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Preset Profile</p>
                <p className="font-semibold text-foreground">{job.preset}</p>
              </div>
              
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Est. Cut Time</p>
                <p className="font-semibold text-foreground">{job.estimatedCutTime} min</p>
              </div>
              
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Drawing Time</p>
                <p className="font-semibold text-foreground">{job.drawingTime} min</p>
              </div>
            </div>

            {job.actualCutTime && (
              <>
                <Separator className="bg-border" />
                <div className="space-y-1">
                  <p className="text-sm text-muted-foreground">Actual Cut Time</p>
                  <p className="text-lg font-bold text-primary">{job.actualCutTime} min</p>
                </div>
              </>
            )}
          </CardContent>
        </Card>

        {/* Parts List Card */}
        <Card className="border-border bg-card shadow-elevation-1">
          <CardHeader>
            <CardTitle className="text-foreground">Parts List</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {job.parts.map((part, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between rounded-lg bg-secondary p-3"
                >
                  <span className="text-sm font-medium text-foreground">{part.name}</span>
                  <Badge variant="outline">×{part.quantity}</Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* DXF Files Card */}
        <Card className="border-border bg-card shadow-elevation-1">
          <CardHeader>
            <CardTitle className="text-foreground">DXF Files</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {job.dxfFiles.map((file, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between rounded-lg bg-secondary p-3"
                >
                  <div className="flex items-center gap-2">
                    <FileText className="h-4 w-4 text-primary" />
                    <span className="text-sm text-foreground">{file}</span>
                  </div>
                  <Button variant="ghost" size="sm">
                    <Download className="h-4 w-4" />
                  </Button>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Action Bar */}
      <div className="fixed bottom-0 left-0 right-0 border-t border-border bg-card p-4 shadow-elevation-3">
        <div className="flex flex-wrap gap-2">
          <Button variant="outline" onClick={onEdit} className="flex-1">
            <Edit className="mr-2 h-4 w-4" />
            Edit Job
          </Button>

          {job.status === "pending" && (
            <Button onClick={onStart} className="flex-1 bg-primary">
              <Play className="mr-2 h-4 w-4" />
              Start Job
            </Button>
          )}

          {job.status === "running" && (
            <>
              <Button variant="secondary" onClick={onPause} className="flex-1">
                <Pause className="mr-2 h-4 w-4" />
                Pause
              </Button>
              <Button onClick={onComplete} className="flex-1 bg-status-complete">
                <CheckCircle className="mr-2 h-4 w-4" />
                Complete
              </Button>
            </>
          )}

          {job.status === "paused" && (
            <Button onClick={onStart} className="flex-1 bg-primary">
              <Play className="mr-2 h-4 w-4" />
              Resume
            </Button>
          )}
        </div>
      </div>
    </div>
  );
};
