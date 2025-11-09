import { useState } from "react";
import { ListChecks, FolderKanban } from "lucide-react";
import { TopBar } from "@/components/TopBar";
import { SettingsDrawer } from "@/components/SettingsDrawer";
import { DashboardCard } from "@/components/DashboardCard";
import { JobCard } from "@/components/JobCard";
import { JobDetailsView } from "@/components/JobDetailsView";
import { StartJobModal } from "@/components/StartJobModal";
import { JobEditModal } from "@/components/JobEditModal";
import { ProjectCard } from "@/components/ProjectCard";
import { ProjectDetailsView } from "@/components/ProjectDetailsView";
import { ProjectEditModal } from "@/components/ProjectEditModal";
import { Job, Project } from "@/types/job";
import { useToast } from "@/hooks/use-toast";

// Mock data for jobs
const mockJobs: Job[] = [
  {
    id: "1",
    projectName: "Steel Brackets - Series A",
    parts: [
      { name: "Bracket-L-100", quantity: 25 },
      { name: "Bracket-R-100", quantity: 25 },
      { name: "Support-Plate", quantity: 10 },
    ],
    rawPlateCount: 3,
    estimatedCutTime: 45,
    drawingTime: 15,
    materialType: "Mild Steel",
    thickness: 3,
    preset: "Steel-3mm-Standard",
    dxfFiles: ["bracket-left.dxf", "bracket-right.dxf", "support.dxf"],
    status: "pending",
  },
  {
    id: "2",
    projectName: "Aluminum Panels - QTY 50",
    parts: [
      { name: "Panel-A-200x400", quantity: 50 },
    ],
    rawPlateCount: 5,
    estimatedCutTime: 60,
    drawingTime: 20,
    materialType: "Aluminum",
    thickness: 2,
    preset: "Aluminum-2mm-Fine",
    dxfFiles: ["panel-a.dxf"],
    status: "running",
    startedAt: new Date(),
  },
  {
    id: "3",
    projectName: "Custom Fabrication - Client XYZ",
    parts: [
      { name: "Custom-Part-001", quantity: 5 },
      { name: "Custom-Part-002", quantity: 10 },
      { name: "Custom-Part-003", quantity: 8 },
      { name: "Custom-Part-004", quantity: 12 },
    ],
    rawPlateCount: 2,
    estimatedCutTime: 35,
    drawingTime: 12,
    materialType: "Stainless Steel",
    thickness: 1.5,
    preset: "Stainless-1.5mm-Precision",
    dxfFiles: ["custom-001.dxf", "custom-002.dxf", "custom-003.dxf", "custom-004.dxf"],
    status: "pending",
  },
];

// Mock data for projects
const mockProjects: Project[] = [
  {
    id: "p1",
    name: "Enclosure Panels - Series B",
    progress: 60,
    missingData: ["Material Type", "Preset Profile", "DXF Files"],
    parts: [
      { name: "Side-Panel-Left", quantity: 20 },
      { name: "Side-Panel-Right", quantity: 20 },
      { name: "Top-Cover", quantity: 20 },
    ],
    status: "incomplete",
    rawPlateCount: 4,
    estimatedCutTime: 55,
    drawingTime: 18,
  },
  {
    id: "p2",
    name: "Decorative Trim - Stainless",
    progress: 30,
    missingData: ["Thickness", "Raw Plate Count", "Estimated Cut Time", "Preset Profile", "DXF Files"],
    parts: [
      { name: "Trim-A-100mm", quantity: 100 },
      { name: "Trim-B-150mm", quantity: 75 },
    ],
    status: "incomplete",
    materialType: "Stainless Steel",
  },
  {
    id: "p3",
    name: "Prototype Parts - Client ABC",
    progress: 80,
    missingData: ["DXF Files"],
    parts: [
      { name: "Proto-001", quantity: 3 },
      { name: "Proto-002", quantity: 3 },
      { name: "Proto-003", quantity: 2 },
    ],
    status: "unscheduled",
    materialType: "Aluminum",
    thickness: 3,
    preset: "Aluminum-3mm-Standard",
    rawPlateCount: 1,
    estimatedCutTime: 25,
    drawingTime: 10,
  },
];

const Index = () => {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [view, setView] = useState<"dashboard" | "queue" | "projects">("dashboard");
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [startModalOpen, setStartModalOpen] = useState(false);
  const [editJobModalOpen, setEditJobModalOpen] = useState(false);
  const [editProjectModalOpen, setEditProjectModalOpen] = useState(false);
  const [jobs, setJobs] = useState<Job[]>(mockJobs);
  const [projects, setProjects] = useState<Project[]>(mockProjects);
  const { toast } = useToast();

  const handleJobAction = (jobId: string, action: string) => {
    const job = jobs.find(j => j.id === jobId);
    if (!job) return;

    switch (action) {
      case "view":
        setSelectedJob(job);
        setView("queue");
        break;
      case "start":
        setSelectedJob(job);
        setStartModalOpen(true);
        break;
      case "pause":
        setJobs(jobs.map(j => 
          j.id === jobId ? { ...j, status: "paused" as const } : j
        ));
        toast({
          title: "Job Paused",
          description: `${job.projectName} has been paused.`,
        });
        break;
      case "complete":
        const actualTime = job.startedAt 
          ? Math.round((new Date().getTime() - job.startedAt.getTime()) / 60000)
          : job.estimatedCutTime;
        
        setJobs(jobs.map(j => 
          j.id === jobId 
            ? { ...j, status: "complete" as const, actualCutTime: actualTime, completedAt: new Date() } 
            : j
        ));
        toast({
          title: "Job Completed",
          description: `${job.projectName} finished in ${actualTime} minutes.`,
          variant: "default",
        });
        break;
      case "edit":
        setSelectedJob(job);
        setEditJobModalOpen(true);
        break;
    }
  };

  const confirmStartJob = () => {
    if (!selectedJob) return;
    
    setJobs(jobs.map(j => 
      j.id === selectedJob.id 
        ? { ...j, status: "running" as const, startedAt: new Date() } 
        : j
    ));
    
    toast({
      title: "Job Started",
      description: `${selectedJob.projectName} is now running.`,
    });
    
    setStartModalOpen(false);
    setSelectedJob(null);
  };

  const handleJobEdit = (jobId: string, updatedData: Partial<Job>) => {
    setJobs(jobs.map(j => 
      j.id === jobId ? { ...j, ...updatedData } : j
    ));
  };

  const handleProjectAction = (projectId: string, action: string) => {
    const project = projects.find(p => p.id === projectId);
    if (!project) return;

    switch (action) {
      case "view":
        setSelectedProject(project);
        setView("projects");
        break;
      case "edit":
        setSelectedProject(project);
        setEditProjectModalOpen(true);
        break;
      case "addToQueue":
        // Convert project to job
        const newJob: Job = {
          id: `job-${Date.now()}`,
          projectName: project.name,
          parts: project.parts,
          rawPlateCount: project.rawPlateCount || 0,
          estimatedCutTime: project.estimatedCutTime || 0,
          drawingTime: project.drawingTime || 0,
          materialType: project.materialType || "",
          thickness: project.thickness || 0,
          preset: project.preset || "",
          dxfFiles: project.dxfFiles || [],
          status: "pending",
        };
        
        setJobs([...jobs, newJob]);
        setProjects(projects.filter(p => p.id !== projectId));
        
        toast({
          title: "Added to Queue",
          description: `${project.name} has been added to the job queue.`,
        });
        
        setSelectedProject(null);
        setView("dashboard");
        break;
    }
  };

  const handleProjectEdit = (projectId: string, updatedData: Partial<Project>) => {
    setProjects(projects.map(p => {
      if (p.id === projectId) {
        const updated = { ...p, ...updatedData };
        
        // Recalculate missing data
        const missing: string[] = [];
        if (!updated.materialType) missing.push("Material Type");
        if (!updated.thickness) missing.push("Thickness");
        if (!updated.preset) missing.push("Preset Profile");
        if (!updated.rawPlateCount) missing.push("Raw Plate Count");
        if (!updated.estimatedCutTime) missing.push("Estimated Cut Time");
        if (!updated.dxfFiles || updated.dxfFiles.length === 0) missing.push("DXF Files");
        
        // Recalculate progress
        const totalFields = 6;
        const completedFields = totalFields - missing.length;
        const progress = Math.round((completedFields / totalFields) * 100);
        
        return {
          ...updated,
          missingData: missing,
          progress,
          status: missing.length === 0 ? "unscheduled" as const : "incomplete" as const,
        };
      }
      return p;
    }));
  };

  const queueJobs = jobs.filter(j => j.status !== "complete");

  if (view === "queue" && selectedJob) {
    return (
      <JobDetailsView
        job={selectedJob}
        onBack={() => {
          setSelectedJob(null);
          setView("dashboard");
        }}
        onStart={() => handleJobAction(selectedJob.id, "start")}
        onPause={() => handleJobAction(selectedJob.id, "pause")}
        onComplete={() => {
          handleJobAction(selectedJob.id, "complete");
          setSelectedJob(null);
          setView("dashboard");
        }}
        onEdit={() => handleJobAction(selectedJob.id, "edit")}
      />
    );
  }

  // Projects view with selected project details
  if (view === "projects" && selectedProject) {
    return (
      <ProjectDetailsView
        project={selectedProject}
        onBack={() => {
          setSelectedProject(null);
          setView("dashboard");
        }}
        onAddToQueue={() => handleProjectAction(selectedProject.id, "addToQueue")}
        onEdit={() => handleProjectAction(selectedProject.id, "edit")}
      />
    );
  }

  // Projects list view
  if (view === "projects") {
    return (
      <div className="min-h-screen bg-background">
        <TopBar onMenuClick={() => setDrawerOpen(true)} />
        
        <div className="p-4">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-2xl font-bold text-foreground">Projects</h2>
            <button
              onClick={() => setView("dashboard")}
              className="text-sm text-primary hover:underline"
            >
              Back to Dashboard
            </button>
          </div>

          <div className="space-y-4">
            {projects.map((project) => (
              <ProjectCard
                key={project.id}
                project={project}
                onView={() => handleProjectAction(project.id, "view")}
                onAddToQueue={() => handleProjectAction(project.id, "addToQueue")}
              />
            ))}
          </div>
        </div>

        <SettingsDrawer open={drawerOpen} onOpenChange={setDrawerOpen} />
        <ProjectEditModal
          project={selectedProject}
          open={editProjectModalOpen}
          onOpenChange={setEditProjectModalOpen}
          onSave={handleProjectEdit}
        />
      </div>
    );
  }

  // Queue view with selected job details
  if (view === "queue" && selectedJob) {
    return (
      <JobDetailsView
        job={selectedJob}
        onBack={() => {
          setSelectedJob(null);
          setView("dashboard");
        }}
        onStart={() => handleJobAction(selectedJob.id, "start")}
        onPause={() => handleJobAction(selectedJob.id, "pause")}
        onComplete={() => {
          handleJobAction(selectedJob.id, "complete");
          setSelectedJob(null);
          setView("dashboard");
        }}
        onEdit={() => handleJobAction(selectedJob.id, "edit")}
      />
    );
  }

  // Queue list view
  if (view === "queue") {
    return (
      <div className="min-h-screen bg-background">
        <TopBar onMenuClick={() => setDrawerOpen(true)} />
        
        <div className="p-4">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-2xl font-bold text-foreground">Queue</h2>
            <button
              onClick={() => setView("dashboard")}
              className="text-sm text-primary hover:underline"
            >
              Back to Dashboard
            </button>
          </div>

          <div className="space-y-4">
            {queueJobs.map((job) => (
              <JobCard
                key={job.id}
                job={job}
                onView={() => handleJobAction(job.id, "view")}
                onEdit={() => handleJobAction(job.id, "edit")}
                onStart={() => handleJobAction(job.id, "start")}
                onPause={() => handleJobAction(job.id, "pause")}
                onComplete={() => handleJobAction(job.id, "complete")}
              />
            ))}
          </div>
        </div>

        <SettingsDrawer open={drawerOpen} onOpenChange={setDrawerOpen} />
        <StartJobModal
          job={selectedJob}
          open={startModalOpen}
          onOpenChange={setStartModalOpen}
          onConfirm={confirmStartJob}
        />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <TopBar onMenuClick={() => setDrawerOpen(true)} />
      
      <main className="p-4">
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-foreground">Dashboard</h2>
          <p className="text-sm text-muted-foreground">Manage your laser cutting operations</p>
        </div>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <DashboardCard
            title="Queue"
            description="Active and ready jobs"
            icon={ListChecks}
            count={queueJobs.length}
            onClick={() => setView("queue")}
          />
          
          <DashboardCard
            title="Projects"
            description="Unscheduled projects"
            icon={FolderKanban}
            count={projects.length}
            onClick={() => setView("projects")}
          />
        </div>
      </main>

      <SettingsDrawer open={drawerOpen} onOpenChange={setDrawerOpen} />
      <StartJobModal
        job={selectedJob}
        open={startModalOpen}
        onOpenChange={setStartModalOpen}
        onConfirm={confirmStartJob}
      />
      <JobEditModal
        job={selectedJob}
        open={editJobModalOpen}
        onOpenChange={setEditJobModalOpen}
        onSave={handleJobEdit}
      />
      <ProjectEditModal
        project={selectedProject}
        open={editProjectModalOpen}
        onOpenChange={setEditProjectModalOpen}
        onSave={handleProjectEdit}
      />
    </div>
  );
};

export default Index;
