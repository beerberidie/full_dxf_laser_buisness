import { Play, Pause, CheckCircle, Eye, Edit, FileDown } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Job } from "@/types/job";
import { cn } from "@/lib/utils";

interface JobCardProps {
  job: Job;
  onView: () => void;
  onEdit: () => void;
  onStart: () => void;
  onPause: () => void;
  onComplete: () => void;
}

export const JobCard = ({
  job,
  onView,
  onEdit,
  onStart,
  onPause,
  onComplete,
}: JobCardProps) => {
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

  const getStatusText = (status: Job["status"]) => {
    return status.charAt(0).toUpperCase() + status.slice(1);
  };

  return (
    <Card className="border-border bg-card shadow-elevation-1 transition-smooth hover:shadow-elevation-2">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <CardTitle className="text-lg text-foreground">{job.projectName}</CardTitle>
          <Badge className={cn("text-white", getStatusColor(job.status))}>
            {getStatusText(job.status)}
          </Badge>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Job Info Grid */}
        <div className="grid grid-cols-2 gap-3 text-sm">
          <div className="space-y-1">
            <p className="text-muted-foreground">Material</p>
            <p className="font-semibold text-foreground">
              {job.materialType} - {job.thickness}mm
            </p>
          </div>
          
          <div className="space-y-1">
            <p className="text-muted-foreground">Plates</p>
            <p className="font-semibold text-foreground">{job.rawPlateCount}</p>
          </div>
          
          <div className="space-y-1">
            <p className="text-muted-foreground">Est. Cut Time</p>
            <p className="font-semibold text-foreground">{job.estimatedCutTime} min</p>
          </div>
          
          <div className="space-y-1">
            <p className="text-muted-foreground">Preset</p>
            <p className="font-semibold text-foreground">{job.preset}</p>
          </div>
        </div>

        {/* Parts List */}
        <div className="space-y-1">
          <p className="text-sm text-muted-foreground">Parts</p>
          <div className="flex flex-wrap gap-1">
            {job.parts.slice(0, 3).map((part, index) => (
              <Badge key={index} variant="outline" className="text-xs">
                {part.name} (×{part.quantity})
              </Badge>
            ))}
            {job.parts.length > 3 && (
              <Badge variant="outline" className="text-xs">
                +{job.parts.length - 3} more
              </Badge>
            )}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-wrap gap-2 pt-2">
          <Button variant="outline" size="sm" onClick={onView}>
            <Eye className="mr-1 h-3 w-3" />
            View
          </Button>
          
          <Button variant="outline" size="sm" onClick={onEdit}>
            <Edit className="mr-1 h-3 w-3" />
            Edit
          </Button>

          {job.status === "pending" && (
            <Button size="sm" onClick={onStart} className="bg-primary">
              <Play className="mr-1 h-3 w-3" />
              Start
            </Button>
          )}

          {job.status === "running" && (
            <>
              <Button size="sm" variant="secondary" onClick={onPause}>
                <Pause className="mr-1 h-3 w-3" />
                Pause
              </Button>
              <Button size="sm" onClick={onComplete} className="bg-status-complete">
                <CheckCircle className="mr-1 h-3 w-3" />
                Complete
              </Button>
            </>
          )}

          {job.status === "paused" && (
            <Button size="sm" onClick={onStart} className="bg-primary">
              <Play className="mr-1 h-3 w-3" />
              Resume
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
};
