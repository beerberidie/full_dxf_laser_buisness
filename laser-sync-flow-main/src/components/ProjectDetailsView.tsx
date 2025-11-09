import { ArrowLeft, Plus, AlertCircle, Edit } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Project } from "@/types/job";

interface ProjectDetailsViewProps {
  project: Project;
  onBack: () => void;
  onAddToQueue: () => void;
  onEdit: () => void;
}

export const ProjectDetailsView = ({
  project,
  onBack,
  onAddToQueue,
  onEdit,
}: ProjectDetailsViewProps) => {
  const isComplete = project.missingData.length === 0;

  return (
    <div className="min-h-screen bg-background pb-24">
      {/* Header */}
      <div className="sticky top-0 z-10 border-b border-border bg-card shadow-elevation-2">
        <div className="flex items-center gap-3 p-4">
          <Button variant="ghost" size="icon" onClick={onBack}>
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <h1 className="flex-1 text-lg font-bold text-foreground">{project.name}</h1>
          <Badge variant={isComplete ? "default" : "secondary"} className={isComplete ? "bg-status-complete" : ""}>
            {project.status === "unscheduled" ? "Unscheduled" : "Incomplete"}
          </Badge>
        </div>
      </div>

      {/* Content */}
      <div className="space-y-4 p-4">
        {/* Progress Card */}
        <Card className="border-border bg-card shadow-elevation-1">
          <CardHeader>
            <CardTitle className="text-foreground">Completion Status</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Progress</span>
                <span className="text-2xl font-bold text-primary">{project.progress}%</span>
              </div>
              <Progress value={project.progress} className="h-3" />
            </div>

            {project.missingData.length > 0 && (
              <>
                <div className="flex items-center gap-2 pt-2">
                  <AlertCircle className="h-5 w-5 text-destructive" />
                  <span className="font-semibold text-foreground">Missing Information</span>
                </div>
                <div className="flex flex-wrap gap-2">
                  {project.missingData.map((item, index) => (
                    <Badge key={index} variant="outline" className="border-destructive text-destructive">
                      {item}
                    </Badge>
                  ))}
                </div>
              </>
            )}
          </CardContent>
        </Card>

        {/* Current Data Card */}
        <Card className="border-border bg-card shadow-elevation-1">
          <CardHeader>
            <CardTitle className="text-foreground">Project Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              {project.materialType && (
                <div className="space-y-1">
                  <p className="text-sm text-muted-foreground">Material Type</p>
                  <p className="font-semibold text-foreground">{project.materialType}</p>
                </div>
              )}
              
              {project.thickness && (
                <div className="space-y-1">
                  <p className="text-sm text-muted-foreground">Thickness</p>
                  <p className="font-semibold text-foreground">{project.thickness} mm</p>
                </div>
              )}
              
              {project.rawPlateCount && (
                <div className="space-y-1">
                  <p className="text-sm text-muted-foreground">Raw Plates</p>
                  <p className="font-semibold text-foreground">{project.rawPlateCount}</p>
                </div>
              )}
              
              {project.preset && (
                <div className="space-y-1">
                  <p className="text-sm text-muted-foreground">Preset Profile</p>
                  <p className="font-semibold text-foreground">{project.preset}</p>
                </div>
              )}
              
              {project.estimatedCutTime && (
                <div className="space-y-1">
                  <p className="text-sm text-muted-foreground">Est. Cut Time</p>
                  <p className="font-semibold text-foreground">{project.estimatedCutTime} min</p>
                </div>
              )}
              
              {project.drawingTime && (
                <div className="space-y-1">
                  <p className="text-sm text-muted-foreground">Drawing Time</p>
                  <p className="font-semibold text-foreground">{project.drawingTime} min</p>
                </div>
              )}
            </div>

            {!project.materialType && !project.preset && (
              <p className="text-sm text-muted-foreground italic">
                No details added yet. Click "Add Details" to complete this project.
              </p>
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
              {project.parts.map((part, index) => (
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

        {/* DXF Files if available */}
        {project.dxfFiles && project.dxfFiles.length > 0 && (
          <Card className="border-border bg-card shadow-elevation-1">
            <CardHeader>
              <CardTitle className="text-foreground">DXF Files</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {project.dxfFiles.map((file, index) => (
                  <Badge key={index} variant="outline">
                    {file}
                  </Badge>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Action Bar */}
      <div className="fixed bottom-0 left-0 right-0 border-t border-border bg-card p-4 shadow-elevation-3">
        <div className="flex gap-2">
          <Button variant="outline" onClick={onEdit} className="flex-1">
            <Edit className="mr-2 h-4 w-4" />
            Add Details
          </Button>

          {isComplete && (
            <Button onClick={onAddToQueue} className="flex-1 bg-primary">
              <Plus className="mr-2 h-4 w-4" />
              Add to Queue
            </Button>
          )}
        </div>
      </div>
    </div>
  );
};
