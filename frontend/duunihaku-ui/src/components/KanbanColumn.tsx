import { useState } from "react";
import { DragDropContext, Droppable, Draggable } from "@hello-pangea/dnd";
import {
  Card,
  Text,
  Paper,
  ScrollArea,
  Badge,
  Group,
  Title,
  Modal,
  Button,
  Menu,
  ActionIcon,
  useMantineTheme,
} from "@mantine/core";

import {
  IconDotsVertical,
  IconExternalLink,
  IconNote,
  IconInfoCircle,
} from "@tabler/icons-react";

import type { Job } from "../api/jobs";
import { useJobs } from "../hooks/useJobs";
import { useQueryClient } from "@tanstack/react-query";

const COLUMN_ORDER = [
  "new",
  "saved",
  "applied",
  "interview",
  "offer",
  "rejected",
];

const COLUMN_LABELS: Record<string, string> = {
  new: "Inbox",
  saved: "Saved",
  applied: "Applied",
  interview: "Interview",
  offer: "Offer",
  rejected: "Rejected",
};

export function KanbanBoard() {
  const theme = useMantineTheme();
  const queryClient = useQueryClient();
  const { jobs, setStateMutation } = useJobs();

  const [selectedJob, setSelectedJob] = useState<Job | null>(null);

  if (jobs.isLoading) return <>Loading...</>;
  if (!jobs.data) return <>No jobs</>;

  // Group jobs by state
  const grouped: Record<string, Job[]> = Object.fromEntries(
    COLUMN_ORDER.map((c) => [c, []]),
  );

  jobs.data.forEach((job) => {
    grouped[job.state ?? "new"].push(job);
  });

  function onDragEnd(result: any) {
    if (!result.destination) return;

    const jobId = result.draggableId.replace("job-", "");
    const newState = result.destination.droppableId;

    // Optimistic update
    queryClient.setQueryData<Job[]>(["jobs"], (old) =>
      old
        ? old.map((j) => (j.id === jobId ? { ...j, state: newState } : j))
        : old,
    );

    setStateMutation.mutate(
      { id: String(jobId), state: newState },
      {
        onSettled: () =>
          setTimeout(() => queryClient.invalidateQueries(["jobs"]), 150),
      },
    );
  }

  return (
    <>
      {/* ---------- MODAL ---------- */}
      <Modal
        opened={!!selectedJob}
        onClose={() => setSelectedJob(null)}
        size="lg"
        title={selectedJob?.title}
      >
        {selectedJob && (
          <>
            <Text fw={600} mb="xs">
              {selectedJob.company}
            </Text>

            <ScrollArea h={300} mb="md">
              <Text size="sm" style={{ whiteSpace: "pre-line" }}>
                {selectedJob.description ||
                  selectedJob.long_description ||
                  selectedJob.full_description ||
                  selectedJob.content ||
                  "No description available."}
              </Text>
            </ScrollArea>

            <Button
              variant="light"
              component="a"
              href={selectedJob.url}
              target="_blank"
            >
              Open Job Posting
            </Button>

            {selectedJob.notes && (
              <Text size="xs" mt="md" c="gray">
                📝 Notes: {selectedJob.notes}
              </Text>
            )}
          </>
        )}
      </Modal>

      {/* ---------- BOARD ---------- */}
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
                      {grouped[col].map((job, index) => (
                        <Draggable
                          key={`job-${job.id}`}
                          draggableId={`job-${job.id}`}
                          index={index}
                        >
                          {(prov, snapshot) => {
                            const dragStyle = prov.draggableProps.style || {};
                            const transform =
                              (dragStyle.transform || "") +
                              (snapshot.isDragging ? " scale(1.05)" : "");

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
                                  ...dragStyle,
                                  transform,
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
                                  cursor: snapshot.isDragging
                                    ? "grabbing"
                                    : "pointer",
                                  boxShadow: snapshot.isDragging
                                    ? theme.shadows.md
                                    : "none",
                                }}
                              >
                                {/* Header row with menu */}
                                <Group position="apart" noWrap>
                                  <Text fw={600} size="sm">
                                    {job.title}
                                  </Text>

                                  <Menu
                                    withinPortal
                                    position="bottom-end"
                                    shadow="md"
                                    width={180}
                                  >
                                    <Menu.Target>
                                      <ActionIcon
                                        variant="subtle"
                                        onClick={(e) => e.stopPropagation()}
                                      >
                                        <IconDotsVertical size={18} />
                                      </ActionIcon>
                                    </Menu.Target>

                                    <Menu.Dropdown>
                                      <Menu.Item
                                        icon={<IconInfoCircle size={14} />}
                                        onClick={(e) => {
                                          e.stopPropagation();
                                          setTimeout(
                                            () => setSelectedJob(job),
                                            0,
                                          );
                                        }}
                                      >
                                        View Description
                                      </Menu.Item>

                                      <Menu.Item icon={<IconNote size={14} />}>
                                        Edit Notes (coming soon)
                                      </Menu.Item>

                                      <Menu.Item
                                        icon={<IconExternalLink size={14} />}
                                        component="a"
                                        href={job.url}
                                        target="_blank"
                                      >
                                        Open Posting
                                      </Menu.Item>
                                    </Menu.Dropdown>
                                  </Menu>
                                </Group>

                                <Text size="xs" c="dimmed">
                                  {job.company}
                                </Text>

                                {job.notes && (
                                  <Text size="xs" mt={6} color="gray">
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
    </>
  );
}
