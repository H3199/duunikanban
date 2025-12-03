import { useState } from "react";
import { DragDropContext, Droppable, Draggable } from "@hello-pangea/dnd";
import {
  Card,
  Text,
  Paper,
  ScrollArea,
  Badge,
  Group,
  Select,
  useMantineTheme,
} from "@mantine/core";
import type { Job } from "../api/jobs";
import { useJobs } from "../hooks/useJobs";
import { fetchCredits } from "../api/jobsApi";
import { flagFromCountry } from "../utils/flagFromCountry";
import { useQuery } from "@tanstack/react-query";
import { APP_VERSION } from "../version";

const COLUMN_ORDER = [
  "new",
  "saved",
  "applied",
  "interview",
  "rejected",
  "trash",
];

const TIME_FILTERS = [
  { value: "", label: "All" },
  { value: "12h", label: "Last 12h" },
  { value: "24h", label: "Last 24h" },
  { value: "48h", label: "Last 48h" },
  { value: "7d", label: "Last 7 days" },
];

function createClickGuard() {
  let moved = false;
  return {
    onMouseDown() {
      moved = false;
    },
    onMouseMove() {
      moved = true;
    },
    shouldClick() {
      return !moved;
    },
  };
}

export function KanbanBoard() {
  const theme = useMantineTheme();

  // ➜ NEW: keep filter state
  const [inboxFilter, setInboxFilter] = useState<string | undefined>(undefined);

  // ➜ UPDATED: pass filter to hook (backend already supports it)
  const { jobs, setStateMutation } = useJobs(inboxFilter);

  if (jobs.isLoading) return <>Loading...</>;
  if (!jobs.data) return <>No jobs</>;

  const grouped = Object.fromEntries(COLUMN_ORDER.map((c) => [c, [] as Job[]]));

  jobs.data.forEach((job: Job) => {
    const state =
      job.state && COLUMN_ORDER.includes(job.state) ? job.state : "new";
    grouped[state].push(job);
  });

  Object.keys(grouped).forEach((state) => {
    grouped[state].sort((a, b) => {
      const tsA = a.updated_at ? new Date(a.updated_at).getTime() : 0;
      const tsB = b.updated_at ? new Date(b.updated_at).getTime() : 0;
      return tsB - tsA;
    });
  });

  function onDragEnd(result: any) {
    if (!result.destination) return;
    const jobId = result.draggableId.replace("job-", "");
    const newState = result.destination.droppableId;
    setStateMutation.mutate({ id: String(jobId), state: newState });
  }

  const COLUMN_LABELS: Record<string, string> = {
    new: "Inbox",
    saved: "Saved",
    applied: "Applied",
    interview: "Interview",
    rejected: "Rejected",
    trash: "Trash",
  };

  return (
    <ScrollArea h="85vh">
      <div
        style={{ textAlign: "center", padding: "0.5rem 0.5rem", opacity: 0.8 }}
      >
        <small>v{APP_VERSION}</small>
        <CreditsFooter />
      </div>
      <DragDropContext onDragEnd={onDragEnd}>
        <div
          style={{
            display: "flex",
            gap: "1.5rem",
            alignItems: "flex-start",
            padding: "1rem 2rem 2rem 0",
          }}
        >
          {COLUMN_ORDER.map((col) => (
            <Droppable droppableId={col} key={col}>
              {(provided) => (
                <Paper
                  ref={provided.innerRef}
                  {...provided.droppableProps}
                  shadow="sm"
                  radius="lg"
                  p="sm"
                  style={{
                    minWidth: 280,
                    maxWidth: 400,
                    minHeight: 450,
                    background: theme.colors.dark[6],
                    border: `1px solid ${theme.colors.dark[3]}`,
                    borderRadius: "14px",
                    display: "flex",
                    flexDirection: "column",
                    overflow: "hidden",
                  }}
                >
                  <div
                    style={{
                      width: "100%",
                      display: "flex",
                      flexDirection: "column",
                      alignItems: "center",
                      justifyContent: "center",
                      marginBottom: "8px",
                    }}
                  >
                    <Text
                      fw={600}
                      size="sm"
                      style={{ color: theme.colors.gray[3] }}
                    >
                      {COLUMN_LABELS[col].toUpperCase()}
                    </Text>

                    <Badge
                      size="xl"
                      radius="sm"
                      styles={{
                        root: {
                          marginTop: "6px",
                          padding: "6px 12px",
                          fontSize: "1.2rem",
                          fontWeight: 700,
                          background: theme.colors.dark[4],
                          color: theme.white,
                        },
                      }}
                    >
                      {grouped[col].length}
                    </Badge>

                    {/* ➜ Only for inbox column */}
                    {col === "new" && (
                      <Select
                        size="xs"
                        mt={6}
                        value={inboxFilter ?? ""}
                        placeholder="Filter inbox"
                        onChange={(v) => setInboxFilter(v || undefined)}
                        data={TIME_FILTERS}
                        style={{ width: "90%", marginTop: "6px" }}
                      />
                    )}
                  </div>

                  <ScrollArea style={{ flex: 1 }} scrollbarSize={6}>
                    <div
                      style={{
                        display: "flex",
                        flexDirection: "column",
                        gap: "8px",
                      }}
                    >
                      {grouped[col].map((job, index) => (
                        <Draggable
                          key={`job-${job.id}`}
                          draggableId={`job-${job.id}`}
                          index={index}
                        >
                          {(prov, snapshot) => {
                            const guard = createClickGuard();
                            return (
                              <Card
                                p="sm"
                                radius="md"
                                withBorder
                                shadow={snapshot.isDragging ? "md" : "xs"}
                                ref={prov.innerRef}
                                {...prov.draggableProps}
                                {...prov.dragHandleProps}
                                style={{
                                  ...prov.draggableProps.style,
                                  transition: "all 0.14s ease",
                                  cursor: snapshot.isDragging
                                    ? "grabbing"
                                    : "pointer",
                                  background: theme.colors.dark[5],
                                  borderRadius: "10px",
                                  border: `1px solid ${theme.colors.dark[4]}`,
                                  boxShadow: snapshot.isDragging
                                    ? "0 6px 18px rgba(0,0,0,0.35)"
                                    : "0 1px 4px rgba(0,0,0,0.15)",
                                }}
                                onMouseDown={guard.onMouseDown}
                                onMouseMove={guard.onMouseMove}
                                onClick={() =>
                                  guard.shouldClick() &&
                                  window.open(`/job/${job.id}`, "_blank")
                                }
                              >
                                <Group gap="xs">
                                  <Text size="lg">
                                    {flagFromCountry(job.country)}
                                  </Text>
                                  <Text
                                    fw={600}
                                    size="sm"
                                    style={{ color: theme.white }}
                                  >
                                    {job.title}
                                  </Text>
                                </Group>
                                <Text
                                  size="xs"
                                  style={{ color: theme.colors.gray[4] }}
                                >
                                  {job.company}
                                </Text>

                                {job.notes && (
                                  <Text
                                    size="xs"
                                    mt={6}
                                    style={{ color: theme.colors.gray[5] }}
                                  >
                                    📝 {job.notes}
                                  </Text>
                                )}
                              </Card>
                            );
                          }}
                        </Draggable>
                      ))}
                      {provided.placeholder}
                    </div>
                  </ScrollArea>
                </Paper>
              )}
            </Droppable>
          ))}
        </div>
      </DragDropContext>
    </ScrollArea>
  );
}

export function CreditsFooter() {
  const { data, isLoading } = useQuery({
    queryKey: ["credits"],
    queryFn: fetchCredits,
    refetchInterval: 60000,
  });

  return (
    <Text
      size="xs"
      style={{ marginTop: "8px", textAlign: "center", opacity: 0.6 }}
    >
      {isLoading ? "Checking API credits..." : `${data} credits remaining`}
    </Text>
  );
}
