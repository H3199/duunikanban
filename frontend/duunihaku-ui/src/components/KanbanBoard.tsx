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
import type { Job } from "../api/jobs.ts";
import { useJobs } from "../hooks/useJobs.ts";

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

  const grouped = Object.fromEntries(COLUMN_ORDER.map((c) => [c, [] as Job[]]));

  jobs.data.forEach((job: Job) => {
    grouped[job.state].push(job);
  });

  function onDragEnd(result: any) {
    if (!result.destination) return;

    const jobId = Number(result.draggableId.replace("job-", ""));
    const newState = result.destination.droppableId;

    setStateMutation.mutate({ id: jobId, state: newState });
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
                  radius="md"
                  p="sm"
                  style={{
                    width: 280,
                    minHeight: 450,
                    background: theme.colors.gray[0],
                    display: "flex",
                    flexDirection: "column",
                  }}
                >
                  <Group position="apart" mb="sm">
                    <Title order={4}>{COLUMN_LABELS[col]}</Title>
                    <Badge>{grouped[col].length}</Badge>
                  </Group>

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
                                radius="md"
                                withBorder
                                shadow={snapshot.isDragging ? "md" : "xs"}
                                ref={prov.innerRef}
                                {...prov.draggableProps}
                                {...prov.dragHandleProps}
                                style={{
                                  ...prov.draggableProps.style,
                                  transition: snapshot.isDragging
                                    ? "transform 0.15s ease"
                                    : "transform 0.20s ease",
                                  cursor: snapshot.isDragging
                                    ? "grabbing"
                                    : "pointer",
                                  background: theme.colors.gray[1],
                                }}
                                onMouseDown={guard.onMouseDown}
                                onMouseMove={guard.onMouseMove}
                                onClick={() => {
                                  if (guard.shouldClick()) {
                                    window.open(`/job/${job.id}`, "_blank");
                                  }
                                }}
                              >
                                <Text fw={600}>{job.title}</Text>
                                <Text size="sm" c="dimmed">
                                  {job.company}
                                </Text>
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
