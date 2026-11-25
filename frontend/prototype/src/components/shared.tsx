import type { ReactNode } from "react";
import { useI18n } from "../i18n/provider";
import {
  Dialog,
  DialogContent,
  DialogTitle,
  DialogDescription,
  DialogClose,
} from "./ui/dialog";
import { Button } from "./ui/button";
export function Heading({
  title,
  subtitle,
}: {
  title: string;
  subtitle: string;
}) {
  return (
    <div className="heading">
      <div>
        <div className="eyebrow" dir="ltr">
          NIKWAY LEARNING OS
        </div>
        <h1>{title}</h1>
        <div className="muted">{subtitle}</div>
      </div>
    </div>
  );
}
export function Card({
  children,
  className = "",
  ...props
}: React.ComponentProps<"section">) {
  return (
    <section className={`card ${className}`} {...props}>
      {children}
    </section>
  );
}
export function Progress({ value, label }: { value: number; label: string }) {
  return (
    <div
      className="bar"
      role="progressbar"
      aria-valuenow={value}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-label={label}
    >
      <i style={{ width: `${value}%` }} />
    </div>
  );
}
export function Modal({
  open,
  onClose,
  title,
  description,
  children,
}: {
  open: boolean;
  onClose: () => void;
  title: string;
  description: string;
  children: ReactNode;
}) {
  const { t, locale } = useI18n();
  return (
    <Dialog
      open={open}
      onOpenChange={(v) => {
        if (!v) onClose();
      }}
    >
      <DialogContent
        className="nikway-dialog"
        dir={locale === "fa" ? "rtl" : "ltr"}
        showCloseButton={false}
      >
        <DialogTitle>{title}</DialogTitle>
        <DialogDescription className="muted">{description}</DialogDescription>
        {children}
        <DialogClose asChild>
          <Button variant="outline" className="justify-self-end">
            {t("بستن", "Close")}
          </Button>
        </DialogClose>
      </DialogContent>
    </Dialog>
  );
}
