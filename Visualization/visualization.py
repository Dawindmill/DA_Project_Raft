import pygame

NAME = "Raft Visualization"

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 1000
FRAME_PER_SECOND = 60

WHITE = (225, 225, 225)

NODE_IMAGE = "assets/node.png"
MESSAGE_IMAGE = "assets/message.png"

class Image:
    x = 0
    y = 0
    image = None
    height = 0
    width = 0
    def __init__(self, image, center_x, center_y, height, width):
        self.x = center_x
        self.y = center_y
        self.height = height
        self.width = width
        self.image = pygame.transform.scale(image, (width, height))

    def render(self, screen):
        screen.blit(self.image, (self.x - self.width//2, self.y - self.height//2))


class Node(Image):
    def __init__(self, image, center_x, center_y):
        width, height = image.get_rect().size
        super().__init__(image, center_x, center_y, height // 10, width // 10)


class Message(Image):
    source = None
    dest = None
    def __init__(self, image, source, dest):
        width, height = image.get_rect().size
        self.source = source
        self.dest = dest
        super().__init__(image, source.x, source.y, height // 15, width // 15)

    def move(self):
        if (self.x, self.y) != (self.dest.x, self.dest.y):
            self.x += (self.dest.x - self.source.x)//100
            self.y += (self.dest.y - self.source.y)//100
            return False
        return True




def start(screen, node_image, message_image, clock):
    done = False

    x = 100
    y = 100

    node1 = Node(node_image, 100, 100)
    node2 = Node(node_image, 400, 100)
    node3 = Node(node_image, 100, 400)
    node_list = [node1, node2, node3]
    message1 = Message(message_image,node1,node2)
    message2 = Message(message_image,node1,node3)
    message_list = [message1]
    a = 0
    while not done:
        screen.fill((255,255,255))
        '''node1.render(screen)
        node2.render(screen)
        node3.render(screen)
        message1.move()
        message1.render(screen)
        message2.move()
        message2.render(screen)'''
        for node in node_list:
            node.render(screen)
        for message in message_list:
            arrived = message.move()
            message.render(screen)
            if arrived:
                message_list.remove(message)
        if (a == 15):
            message_list.append(message2)
        a+=1
        #pygame.draw.rect(screen, (255,0,0), pygame.Rect((x,y), (100,100)))
        #if (x != 400):
        #    x+=2
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

        pygame.display.flip()
        clock.tick(FRAME_PER_SECOND)


def main():
    pygame.__init__(NAME)
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.fill(WHITE)
    node_image = pygame.image.load(NODE_IMAGE)
    message_image = pygame.image.load(MESSAGE_IMAGE)
    clock = pygame.time.Clock()
    start(screen, node_image, message_image, clock)

if __name__ == "__main__":
    main()