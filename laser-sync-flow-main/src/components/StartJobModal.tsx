import { CheckCircle, FileText, Layers, Clock, Wrench } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Job } from "@/types/job";

interface StartJobModalProps {
  job: Job | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onConfirm: () => void;
}

export const StartJobModal = ({
  job,
  open,
  onOpenChange,
  onConfirm,
}: StartJobModalProps) => {
  if (!job) return null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md border-border bg-card">
        <DialogHeader>
          <DialogTitle className="text-foreground">Confirm Job Start</DialogTitle>
          <DialogDescription className="text-muted-foreground">
            Review job details before proceeding
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {/* Job Name */}
          <div>
            <h3 className="mb-2 text-lg font-bold text-primary">{job.projectName}</h3>
          </div>

          {/* Quick Info Grid */}
          <div className="grid grid-cols-2 gap-3 rounded-lg bg-secondary p-4">
            <div className="flex items-center gap-2">
              <Wrench className="h-4 w-4 text-primary" />
              <div>
                <p className="text-xs text-muted-foreground">Preset</p>
                <p className="text-sm font-semibold text-foreground">{job.preset}</p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <Layers className="h-4 w-4 text-primary" />
              <div>
                <p className="text-xs text-muted-foreground">Plates</p>
                <p className="text-sm font-semibold text-foreground">{job.rawPlateCount}</p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <Clock className="h-4 w-4 text-primary" />
              <div>
                <p className="text-xs text-muted-foreground">Est. Time</p>
                <p className="text-sm font-semibold text-foreground">{job.estimatedCutTime} min</p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <FileText className="h-4 w-4 text-primary" />
              <div>
                <p className="text-xs text-muted-foreground">Files</p>
                <p className="text-sm font-semibold text-foreground">{job.dxfFiles.length}</p>
              </div>
            </div>
          </div>

          {/* Material Info */}
          <div className="rounded-lg border border-border p-3">
            <p className="mb-1 text-xs text-muted-foreground">Material</p>
            <p className="text-sm font-semibold text-foreground">
              {job.materialType} - {job.thickness}mm
            </p>
          </div>

          {/* Parts Preview */}
          <div>
            <p className="mb-2 text-xs text-muted-foreground">Parts ({job.parts.length})</p>
            <div className="flex flex-wrap gap-1">
              {job.parts.slice(0, 4).map((part, index) => (
                <Badge key={index} variant="outline" className="text-xs">
                  {part.name} (×{part.quantity})
                </Badge>
              ))}
              {job.parts.length > 4 && (
                <Badge variant="outline" className="text-xs">
                  +{job.parts.length - 4} more
                </Badge>
              )}
            </div>
          </div>
        </div>

        <DialogFooter className="gap-2">
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button onClick={onConfirm} className="bg-primary">
            <CheckCircle className="mr-2 h-4 w-4" />
            Start Job
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};
