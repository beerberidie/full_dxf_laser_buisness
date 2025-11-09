import { useState, useEffect } from "react";
import { Plus, Trash2, Save } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Project } from "@/types/job";
import { jobFormSchema, JobFormValues } from "@/lib/jobValidation";
import { useToast } from "@/hooks/use-toast";

interface ProjectEditModalProps {
  project: Project | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSave: (projectId: string, updatedData: Partial<Project>) => void;
}

export const ProjectEditModal = ({
  project,
  open,
  onOpenChange,
  onSave,
}: ProjectEditModalProps) => {
  const { toast } = useToast();
  const [formData, setFormData] = useState<JobFormValues | null>(null);
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (project) {
      setFormData({
        projectName: project.name,
        materialType: project.materialType || "",
        thickness: project.thickness || 0,
        rawPlateCount: project.rawPlateCount || 0,
        estimatedCutTime: project.estimatedCutTime || 0,
        drawingTime: project.drawingTime || 0,
        preset: project.preset || "",
        parts: project.parts,
        dxfFiles: project.dxfFiles || [""],
      });
      setErrors({});
    }
  }, [project]);

  if (!project || !formData) return null;

  const handleInputChange = (field: keyof JobFormValues, value: any) => {
    setFormData({ ...formData, [field]: value });
    if (errors[field]) {
      setErrors({ ...errors, [field]: "" });
    }
  };

  const handlePartChange = (index: number, field: "name" | "quantity", value: string | number) => {
    const newParts = [...formData.parts];
    if (field === "name") {
      newParts[index] = { ...newParts[index], name: value as string };
    } else {
      newParts[index] = { ...newParts[index], quantity: value as number };
    }
    setFormData({ ...formData, parts: newParts });
  };

  const addPart = () => {
    setFormData({
      ...formData,
      parts: [...formData.parts, { name: "", quantity: 1 }],
    });
  };

  const removePart = (index: number) => {
    if (formData.parts.length > 1) {
      const newParts = formData.parts.filter((_, i) => i !== index);
      setFormData({ ...formData, parts: newParts });
    }
  };

  const handleDxfFileChange = (index: number, value: string) => {
    const newFiles = [...formData.dxfFiles];
    newFiles[index] = value;
    setFormData({ ...formData, dxfFiles: newFiles });
  };

  const addDxfFile = () => {
    setFormData({
      ...formData,
      dxfFiles: [...formData.dxfFiles, ""],
    });
  };

  const removeDxfFile = (index: number) => {
    if (formData.dxfFiles.length > 1) {
      const newFiles = formData.dxfFiles.filter((_, i) => i !== index);
      setFormData({ ...formData, dxfFiles: newFiles });
    }
  };

  const handleSave = () => {
    try {
      const validated = jobFormSchema.parse(formData);
      
      // Save with validated data
      onSave(project.id, {
        name: validated.projectName,
        materialType: validated.materialType,
        thickness: validated.thickness,
        rawPlateCount: validated.rawPlateCount,
        estimatedCutTime: validated.estimatedCutTime,
        drawingTime: validated.drawingTime,
        preset: validated.preset,
        parts: validated.parts as { name: string; quantity: number }[],
        dxfFiles: validated.dxfFiles,
      });

      toast({
        title: "Project Updated",
        description: "Changes synced to PC successfully.",
      });

      onOpenChange(false);
    } catch (error: any) {
      if (error.errors) {
        const fieldErrors: Record<string, string> = {};
        error.errors.forEach((err: any) => {
          const field = err.path.join(".");
          fieldErrors[field] = err.message;
        });
        setErrors(fieldErrors);
        
        toast({
          title: "Validation Error",
          description: "Please check the form for errors.",
          variant: "destructive",
        });
      }
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] border-border bg-card">
        <DialogHeader>
          <DialogTitle className="text-foreground">Add Project Details</DialogTitle>
          <DialogDescription className="text-muted-foreground">
            Complete missing information to add this project to the queue.
          </DialogDescription>
        </DialogHeader>

        <ScrollArea className="max-h-[60vh] pr-4">
          <div className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="projectName" className="text-foreground">Project Name</Label>
              <Input
                id="projectName"
                value={formData.projectName}
                onChange={(e) => handleInputChange("projectName", e.target.value)}
                className={errors.projectName ? "border-destructive" : ""}
              />
              {errors.projectName && (
                <p className="text-xs text-destructive">{errors.projectName}</p>
              )}
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="materialType" className="text-foreground">Material Type</Label>
                <Input
                  id="materialType"
                  value={formData.materialType}
                  onChange={(e) => handleInputChange("materialType", e.target.value)}
                  className={errors.materialType ? "border-destructive" : ""}
                />
                {errors.materialType && (
                  <p className="text-xs text-destructive">{errors.materialType}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="thickness" className="text-foreground">Thickness (mm)</Label>
                <Input
                  id="thickness"
                  type="number"
                  step="0.1"
                  value={formData.thickness || ""}
                  onChange={(e) => handleInputChange("thickness", parseFloat(e.target.value) || 0)}
                  className={errors.thickness ? "border-destructive" : ""}
                />
                {errors.thickness && (
                  <p className="text-xs text-destructive">{errors.thickness}</p>
                )}
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="preset" className="text-foreground">Preset Profile</Label>
              <Input
                id="preset"
                value={formData.preset}
                onChange={(e) => handleInputChange("preset", e.target.value)}
                className={errors.preset ? "border-destructive" : ""}
              />
              {errors.preset && (
                <p className="text-xs text-destructive">{errors.preset}</p>
              )}
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label htmlFor="rawPlateCount" className="text-foreground">Plate Count</Label>
                <Input
                  id="rawPlateCount"
                  type="number"
                  value={formData.rawPlateCount || ""}
                  onChange={(e) => handleInputChange("rawPlateCount", parseInt(e.target.value) || 0)}
                  className={errors.rawPlateCount ? "border-destructive" : ""}
                />
                {errors.rawPlateCount && (
                  <p className="text-xs text-destructive">{errors.rawPlateCount}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="estimatedCutTime" className="text-foreground">Cut Time (min)</Label>
                <Input
                  id="estimatedCutTime"
                  type="number"
                  value={formData.estimatedCutTime || ""}
                  onChange={(e) => handleInputChange("estimatedCutTime", parseInt(e.target.value) || 0)}
                  className={errors.estimatedCutTime ? "border-destructive" : ""}
                />
                {errors.estimatedCutTime && (
                  <p className="text-xs text-destructive">{errors.estimatedCutTime}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="drawingTime" className="text-foreground">Draw Time (min)</Label>
                <Input
                  id="drawingTime"
                  type="number"
                  value={formData.drawingTime || ""}
                  onChange={(e) => handleInputChange("drawingTime", parseInt(e.target.value) || 0)}
                  className={errors.drawingTime ? "border-destructive" : ""}
                />
                {errors.drawingTime && (
                  <p className="text-xs text-destructive">{errors.drawingTime}</p>
                )}
              </div>
            </div>

            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <Label className="text-foreground">Parts List</Label>
                <Button type="button" variant="outline" size="sm" onClick={addPart}>
                  <Plus className="mr-1 h-3 w-3" />
                  Add Part
                </Button>
              </div>
              
              <div className="space-y-2">
                {formData.parts.map((part, index) => (
                  <div key={index} className="flex gap-2">
                    <Input
                      placeholder="Part name"
                      value={part.name}
                      onChange={(e) => handlePartChange(index, "name", e.target.value)}
                      className="flex-1"
                    />
                    <Input
                      type="number"
                      placeholder="Qty"
                      value={part.quantity}
                      onChange={(e) => handlePartChange(index, "quantity", parseInt(e.target.value) || 1)}
                      className="w-24"
                    />
                    <Button
                      type="button"
                      variant="ghost"
                      size="icon"
                      onClick={() => removePart(index)}
                      disabled={formData.parts.length === 1}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                ))}
              </div>
              {errors.parts && (
                <p className="text-xs text-destructive">{errors.parts}</p>
              )}
            </div>

            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <Label className="text-foreground">DXF Files</Label>
                <Button type="button" variant="outline" size="sm" onClick={addDxfFile}>
                  <Plus className="mr-1 h-3 w-3" />
                  Add File
                </Button>
              </div>
              
              <div className="space-y-2">
                {formData.dxfFiles.map((file, index) => (
                  <div key={index} className="flex gap-2">
                    <Input
                      placeholder="filename.dxf"
                      value={file}
                      onChange={(e) => handleDxfFileChange(index, e.target.value)}
                      className="flex-1"
                    />
                    <Button
                      type="button"
                      variant="ghost"
                      size="icon"
                      onClick={() => removeDxfFile(index)}
                      disabled={formData.dxfFiles.length === 1}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                ))}
              </div>
              {errors.dxfFiles && (
                <p className="text-xs text-destructive">{errors.dxfFiles}</p>
              )}
            </div>
          </div>
        </ScrollArea>

        <DialogFooter className="gap-2">
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button onClick={handleSave} className="bg-primary">
            <Save className="mr-2 h-4 w-4" />
            Save Details
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};
