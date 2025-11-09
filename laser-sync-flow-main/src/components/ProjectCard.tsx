import { AlertCircle, Plus, Eye } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Project } from "@/types/job";

interface ProjectCardProps {
  project: Project;
  onView: () => void;
  onAddToQueue: () => void;
}

export const ProjectCard = ({
  project,
  onView,
  onAddToQueue,
}: ProjectCardProps) => {
  const isComplete = project.missingData.length === 0;

  return (
    <Card className="border-border bg-card shadow-elevation-1 transition-smooth hover:shadow-elevation-2">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <CardTitle className="text-lg text-foreground">{project.name}</CardTitle>
          <Badge
            variant={isComplete ? "default" : "secondary"}
            className={isComplete ? "bg-status-complete" : ""}
          >
            {project.status === "unscheduled" ? "Unscheduled" : "Incomplete"}
          </Badge>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Progress Bar */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Completion</span>
            <span className="font-semibold text-foreground">{project.progress}%</span>
          </div>
          <Progress value={project.progress} className="h-2" />
        </div>

        {/* Missing Data */}
        {project.missingData.length > 0 && (
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <AlertCircle className="h-4 w-4 text-destructive" />
              <span className="text-sm font-medium text-foreground">Missing Information</span>
            </div>
            <div className="flex flex-wrap gap-1">
              {project.missingData.map((item, index) => (
                <Badge key={index} variant="outline" className="text-xs text-destructive border-destructive">
                  {item}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {/* Parts Preview */}
        <div className="space-y-1">
          <p className="text-sm text-muted-foreground">Parts ({project.parts.length})</p>
          <div className="flex flex-wrap gap-1">
            {project.parts.slice(0, 3).map((part, index) => (
              <Badge key={index} variant="outline" className="text-xs">
                {part.name} (×{part.quantity})
              </Badge>
            ))}
            {project.parts.length > 3 && (
              <Badge variant="outline" className="text-xs">
                +{project.parts.length - 3} more
              </Badge>
            )}
          </div>
        </div>

        {/* Existing Data Preview */}
        {(project.materialType || project.preset) && (
          <div className="rounded-lg bg-secondary p-3 text-sm">
            {project.materialType && (
              <p className="text-foreground">
                <span className="text-muted-foreground">Material: </span>
                {project.materialType} {project.thickness && `- ${project.thickness}mm`}
              </p>
            )}
            {project.preset && (
              <p className="text-foreground">
                <span className="text-muted-foreground">Preset: </span>
                {project.preset}
              </p>
            )}
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex flex-wrap gap-2 pt-2">
          <Button variant="outline" size="sm" onClick={onView}>
            <Eye className="mr-1 h-3 w-3" />
            View Details
          </Button>
          
          {isComplete && (
            <Button size="sm" onClick={onAddToQueue} className="bg-primary">
              <Plus className="mr-1 h-3 w-3" />
              Add to Queue
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
};
