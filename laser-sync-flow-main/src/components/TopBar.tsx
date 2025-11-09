import { Menu } from "lucide-react";
import { Button } from "@/components/ui/button";

interface TopBarProps {
  onMenuClick: () => void;
}

export const TopBar = ({ onMenuClick }: TopBarProps) => {
  return (
    <header className="sticky top-0 z-50 w-full border-b border-border bg-card shadow-elevation-2">
      <div className="flex h-16 items-center justify-between px-4">
        <div className="flex-1" />
        
        <h1 className="text-xl font-bold tracking-tight text-primary">
          LASER OS
        </h1>
        
        <div className="flex flex-1 justify-end">
          <Button
            variant="ghost"
            size="icon"
            onClick={onMenuClick}
            className="text-foreground hover:bg-secondary"
          >
            <Menu className="h-6 w-6" />
          </Button>
        </div>
      </div>
    </header>
  );
};
