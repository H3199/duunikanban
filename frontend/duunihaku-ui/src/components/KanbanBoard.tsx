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
        {/* THIS FIXES THE STACKING ISSUE */}
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
                    {grouped[col].map((job, index) => (
                      <Draggable
                        key={`job-${job.id}`}
                        draggableId={`job-${job.id}`}
                        index={index}
                      >
                        {(prov, snapshot) => {
                          // 👇 preserve native drag transform
                          const dragStyle = prov.draggableProps.style || {};
                          const combinedTransform =
                            (dragStyle.transform || "") +
                            (snapshot.isDragging
                              ? " scale(1.05)"
                              : " scale(1)");

                          return (
                            <Card
                              ref={prov.innerRef}
                              {...prov.draggableProps}
                              {...prov.dragHandleProps}
                              withBorder
                              radius="md"
                              mb="md"
                              p="sm"
                              style={{
                                ...dragStyle, // keep positioning from the library
                                transform: combinedTransform, // add our effect on top
                                background: "white",
                                borderLeft: `4px solid ${
                                  {
                                    new: "#adb5bd",
                                    saved: "#4dabf7",
                                    applied: "#228be6",
                                    interview: "#fab005",
                                    offer: "#40c057",
                                    rejected: "#fa5252",
                                  }[job.state] || "#adb5bd"
                                }`,
                                transition: "transform 150ms ease",
                                boxShadow: snapshot.isDragging
                                  ? theme.shadows.md
                                  : "none",
                              }}
                            >
                              <Text fw={600} size="sm" mb={4}>
                                {job.title}
                              </Text>

                              <Text size="xs" c="dimmed" mb={4}>
                                {job.company}
                              </Text>

                              {job.notes && (
                                <Text
                                  size="xs"
                                  mt={4}
                                  style={{ color: theme.colors.gray[6] }}
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
