import { DragDropContext, Droppable, Draggable } from "@hello-pangea/dnd";
import { Card, Text, Paper } from "@mantine/core";
import { Job } from "../types";
import { useJobs } from "../hooks/useJobs";

const COLUMN_ORDER = [
  "new",
  "saved",
  "applied",
  "interview",
  "offer",
  "rejected",
];

export function KanbanBoard() {
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

  return (
    <DragDropContext onDragEnd={onDragEnd}>
      <div style={{ display: "flex", gap: "1rem" }}>
        {COLUMN_ORDER.map((col) => (
          <Droppable droppableId={col} key={col}>
            {(provided) => (
              <Paper
                ref={provided.innerRef}
                {...provided.droppableProps}
                shadow="sm"
                p="sm"
                style={{ width: 260, minHeight: 400 }}
              >
                <Text fw={700} mb="sm">
                  {col.toUpperCase()}
                </Text>

                {grouped[col].map((job: Job, index: number) => (
                  <Draggable
                    key={`job-${job.id}`}
                    draggableId={`job-${job.id}`}
                    index={index}
                  >
                    {(prov) => (
                      <Card
                        ref={prov.innerRef}
                        {...prov.draggableProps}
                        {...prov.dragHandleProps}
                        shadow="md"
                        mb="sm"
                      >
                        <Text fw={600}>{job.title}</Text>
                        <Text size="sm" c="dimmed">
                          {job.company}
                        </Text>
                      </Card>
                    )}
                  </Draggable>
                ))}

                {provided.placeholder}
              </Paper>
            )}
          </Droppable>
        ))}
      </div>
    </DragDropContext>
  );
}
