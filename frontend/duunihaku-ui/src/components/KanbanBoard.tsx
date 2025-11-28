import { DragDropContext, Droppable, Draggable } from "@hello-pangea/dnd";
import {
  Card,
  Text,
  Paper,
  ScrollArea,
  Badge,
  Group,
  Title,
  useMantineTheme,
} from "@mantine/core";
import type { Job } from "../api/jobs";
import { useJobs } from "../hooks/useJobs";
import { fetchCredits } from "../api/jobsApi";
import { flagFromCountry } from "../utils/flagFromCountry";
import { useQuery } from "@tanstack/react-query";

const COLUMN_ORDER = [
  "new",
  "saved",
  "applied",
  "interview",
  "offer",
  "rejected",
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
  const { jobs, setStateMutation } = useJobs();

  if (jobs.isLoading) return <>Loading...</>;
  if (!jobs.data) return <>No jobs</>;

  // ---- FIX: ensure grouping does not break ----
  const grouped = Object.fromEntries(COLUMN_ORDER.map((c) => [c, [] as Job[]]));

  jobs.data.forEach((job: Job) => {
    const state =
      job.state && COLUMN_ORDER.includes(job.state) ? job.state : "new"; // fallback

    grouped[state].push(job);
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
    offer: "Offer",
    rejected: "Rejected",
  };

  return (
    <ScrollArea h="85vh">
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
                  {/* ---- COLUMN HEADER ---- */}
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
                  </div>

                  {/* ---- JOB CARDS ---- */}
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
                                onClick={() => {
                                  if (guard.shouldClick()) {
                                    window.open(`/job/${job.id}`, "_blank");
                                  }
                                }}
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
        <CreditsFooter />
      </DragDropContext>
    </ScrollArea>
  );
}

export function CreditsFooter() {
  const { data, isLoading } = useQuery({
    queryKey: ["credits"],
    queryFn: fetchCredits,
    refetchInterval: 60000, // 1 min auto refresh
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
