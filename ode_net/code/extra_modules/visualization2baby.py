import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib.patches as patches
from figure_saver import save_figure
import numpy as np
import torch
try:
    from torchdiffeq.__init__ import odeint_adjoint as odeint
except ImportError:
    from torchdiffeq import odeint_adjoint as odeint


class Visualizator():

    def visualize(self):
        pass

    def __init__(self, data_handler, odenet, settings):
        self.data_handler = data_handler
        self.odenet = odenet
        self.settings = settings

    def save_plot(self, fig, folder, name):
        fig.savefig('{}/{}.eps'.format(folder, name))

class Visualizator1D(Visualizator):
    
    def __init__(self, data_handler, odenet, settings):
        super().__init__(data_handler, odenet, settings)
        self.fig_dyn = plt.figure(figsize=(6,6))
        self.fig_dyn.canvas.set_window_title("Dynamics")
        self.ax_dyn = self.fig_dyn.add_subplot(111, frameon=False)
        self.fig_traj = plt.figure(figsize=(6,6))
        self.fig_traj.canvas.set_window_title("Trajectories")
        self.ax_traj = self.fig_traj.add_subplot(111, frameon=False)
        self.fig_traj_split = plt.figure(figsize=(12,4))
        self.fig_traj_split.canvas.set_window_title("Trajectories in each dimension")
        self.axes_traj_split = self.fig_traj_split.subplots(nrows=1, ncols=2, sharex=False, subplot_kw={'frameon':True})

        self.legend_traj = [Line2D([0], [0], color='black', linestyle='--', label='NN approximation'),
                Line2D([0], [0], marker='o', color='red', label='Data', markerfacecolor='red', markersize=5)]

        self.fig_traj_split.legend(handles=self.legend_traj, loc='upper center', ncol=2)
        
        self._set_ax_limits()

        #plt.show()
        #plt.savefig('initial_plot.png')
        
    def plot(self):
        #plt.figure(1)
        self.fig_dyn.canvas.draw_idle()
        self.fig_dyn.canvas.start_event_loop(0.005)
        #plt.figure(2)
        self.fig_traj.canvas.draw_idle()
        self.fig_traj.canvas.start_event_loop(0.005)

        self.fig_traj_split.canvas.draw_idle()
        self.fig_traj_split.canvas.start_event_loop(0.005)

    def _set_ax_limits(self):
        data = self.data_handler.data_np
        times = self.data_handler.time_np
        self.EXTRA_WIDTH_TRAJ = 0.2
        self.EXTRA_WIDTH_DYN = 1

        self.x_span = (np.min([np.min(traj[:,:,0]) for traj in data]),
                       np.max([np.max(traj[:,:,0]) for traj in data]))
        self.x_width = self.x_span[1] - self.x_span[0]

        self.xdot_span = (np.min([np.min(traj[:,:,1]) for traj in data]),
                          np.max([np.max(traj[:,:,1]) for traj in data]))
        self.xdot_width = self.xdot_span[1] - self.xdot_span[0]

        self.time_span = (np.min([np.min(time[:]) for time in times]),
                          np.max([np.max(time[:]) for time in times]))
        self.time_width = self.time_span[1] - self.time_span[0]

        self.ax_traj.set_xlim((self.x_span[0]-self.x_width*self.EXTRA_WIDTH_TRAJ,
                               self.x_span[1]+self.x_width*self.EXTRA_WIDTH_TRAJ))
        self.ax_traj.set_ylim((self.xdot_span[0]-self.xdot_width*self.EXTRA_WIDTH_TRAJ,
                               self.xdot_span[1]+self.xdot_width*self.EXTRA_WIDTH_TRAJ))

        self.ax_dyn.set_xlim((self.x_span[0]-self.x_width*self.EXTRA_WIDTH_DYN,
                               self.x_span[1]+self.x_width*self.EXTRA_WIDTH_DYN))
        self.ax_dyn.set_ylim((self.xdot_span[0]-self.xdot_width*self.EXTRA_WIDTH_DYN,
                               self.xdot_span[1]+self.xdot_width*self.EXTRA_WIDTH_DYN))

        for ix, ax in enumerate(self.axes_traj_split):
            ax.set_xlim((self.time_span[0]-self.time_width*self.EXTRA_WIDTH_TRAJ,
                         self.time_span[1]+self.time_width*self.EXTRA_WIDTH_TRAJ))
            if ix == 0:
                ax.set_ylim((self.x_span[0]-self.x_width*self.EXTRA_WIDTH_TRAJ,
                             self.x_span[1]+self.x_width*self.EXTRA_WIDTH_TRAJ))
            if ix == 1:
                ax.set_ylim((self.xdot_span[0]-self.xdot_width*self.EXTRA_WIDTH_TRAJ,
                             self.xdot_span[1]+self.xdot_width*self.EXTRA_WIDTH_TRAJ))

    def visualize(self):
        self.trajectories = self.data_handler.calculate_trajectory(self.odenet, self.settings['method'])
        self._visualize_trajectories_all()
        self._visualize_trajectories_split()
        #self._visualize_dynamics()
        self._set_ax_limits()

    def _visualize_trajectories_all(self):
        self.ax_traj.cla()

        for j in range(self.data_handler.ntraj-1, -1, -1):
            self.ax_traj.plot(self.data_handler.data_np[j][:,:,0].flatten(), self.data_handler.data_np[j][:,:,1].flatten(), 'r-o', alpha=0.3)

        
        for j in range(self.data_handler.ntraj):
            self.ax_traj.plot(self.trajectories[j][:,:,0].numpy().flatten(), self.trajectories[j][:,:,1].numpy().flatten(), 'k--', lw=2)

        
        self.ax_traj.set_xlabel(r'$x$')
        self.ax_traj.set_ylabel(r'$\dot{x}$')
        self.ax_traj.legend(handles=self.legend_traj, loc='upper center', ncol=2)

    def _visualize_trajectories_split(self):
        times = self.data_handler.time_np

        for i, ax in enumerate(self.axes_traj_split):
            ax.cla()
            for j, (approx_traj, traj) in enumerate(zip(self.trajectories, self.data_handler.data_np)):
                ax.plot(times[j].flatten(), traj[:,:,i].flatten(), 'r-o', alpha=0.3)
                ax.plot(times[j].flatten(), approx_traj[:,:,i].numpy().flatten(),'k--', lw=2)
            ax.set_xlabel(r'$t$')
            if i == 0:
                ax.set_ylabel(r'$x$')
            elif i == 1:
                ax.set_ylabel(r'$\dot{x}$')

    def _visualize_dynamics(self):
        GRIDSIZE = 20

        self.ax_dyn.cla()
        for j in range(self.data_handler.ntraj-1, -1, -1):
            self.ax_dyn.plot(self.data_handler.data_np[j][:,:,0].flatten(), self.data_handler.data_np[j][:,:,1].flatten(), '-r', alpha=0.3, linewidth=2)

        xv, yv = torch.meshgrid([torch.linspace(self.x_span[0]-self.x_width*self.EXTRA_WIDTH_DYN, 
                                                self.x_span[1]+self.x_width*self.EXTRA_WIDTH_DYN, 
                                                GRIDSIZE),
                                 torch.linspace(self.xdot_span[0]-self.xdot_width*self.EXTRA_WIDTH_DYN,
                                                self.xdot_span[1]+self.xdot_width*self.EXTRA_WIDTH_DYN, 
                                                GRIDSIZE)])
        inputs = torch.from_numpy(np.vstack([array for array in map(np.ravel, (xv, yv))])).to(self.data_handler.device)
        inputs = torch.transpose(inputs, 1, 0)
        t = torch.zeros(1).to(self.data_handler.device)
        grad = self.odenet.forward(t, inputs)
        grad_x = grad[:, 0].reshape(xv.shape).cpu().numpy()
        grad_y = grad[:, 1].reshape(yv.shape).cpu().numpy()

        self.ax_dyn.quiver(xv, yv, grad_x, grad_y)
        self.ax_dyn.set_xlabel(r'$x$')
        self.ax_dyn.set_ylabel(r'$\dot{x}$')
        self.ax_dyn.legend(handles=self.legend_traj, loc='upper center', ncol=2)

    def save(self, dir, epoch):
         self.fig_dyn.savefig('{}dyn_epoch{}.eps'.format(dir, epoch))
         self.fig_traj.savefig('{}traj_epoch{}.eps'.format(dir, epoch))
         self.fig_traj_split.savefig('{}each_dim_epoch{}.eps'.format(dir, epoch))
         self.fig_dyn.savefig('{}dyn_epoch{}.png'.format(dir, epoch))
         self.fig_traj.savefig('{}traj_epoch{}.png'.format(dir, epoch))
         self.fig_traj_split.savefig('{}each_dim_epoch{}.png'.format(dir, epoch))


class Visualizator2D(Visualizator):
    
    def __init__(self, data_handler, odenet, settings):
        super().__init__(data_handler, odenet, settings)
        self.fig_dyn = plt.figure(figsize=(6,6))
        self.fig_dyn.canvas.set_window_title("Dynamics")
        self.ax_dyn = self.fig_dyn.add_subplot(111, frameon=False)
        self.fig_traj = plt.figure(figsize=(6,6))
        self.fig_traj.canvas.set_window_title("Trajectories")
        self.ax_traj = self.fig_traj.add_subplot(111, frameon=False)
        self.fig_traj_split = plt.figure(figsize=(12,6))
        self.fig_traj_split.canvas.set_window_title("Trajectories in each dimension")
        self.axes_traj_split = self.fig_traj_split.subplots(nrows=2, ncols=2, sharex=False, subplot_kw={'frameon':True})

        self.legend_traj = [Line2D([0], [0], color='black', linestyle='--', label='NN approximation'),
                Line2D([0], [0], marker='o', color='red', label='Data', markerfacecolor='red', markersize=5)]

        self.fig_traj_split.legend(handles=self.legend_traj, loc='upper center', ncol=2)
        
        self._set_ax_limits()

        plt.show(block=True)
        
    def plot(self):
        #plt.figure(1)
        self.fig_dyn.canvas.draw_idle()
        self.fig_dyn.canvas.start_event_loop(0.005)
        #plt.figure(2)
        self.fig_traj.canvas.draw_idle()
        self.fig_traj.canvas.start_event_loop(0.005)

        self.fig_traj_split.canvas.draw_idle()
        self.fig_traj_split.canvas.start_event_loop(0.005)

    def _set_ax_limits(self):
        data = self.data_handler.data_np
        times = self.data_handler.time_np
        self.EXTRA_WIDTH_TRAJ = 0.2
        self.EXTRA_WIDTH_DYN = 1

        self.x_span = (np.min([np.min(traj[:,:,0]) for traj in data]),
                       np.max([np.max(traj[:,:,0]) for traj in data]))
        self.x_width = self.x_span[1] - self.x_span[0]


        self.y_span = (np.min([np.min(traj[:,:,1]) for traj in data]),
                       np.max([np.max(traj[:,:,1]) for traj in data]))
        self.y_width = self.y_span[1] - self.y_span[0]

        self.xdot_span = (np.min([np.min(traj[:,:,2]) for traj in data]),
                          np.max([np.max(traj[:,:,2]) for traj in data]))
        self.xdot_width = self.xdot_span[1] - self.xdot_span[0]

        self.ydot_span = (np.min([np.min(traj[:,:,3]) for traj in data]),
                          np.max([np.max(traj[:,:,3]) for traj in data]))
        self.ydot_width = self.ydot_span[1] - self.ydot_span[0]

        
        self.time_span = (np.min([np.min(time[:]) for time in times]),
                          np.max([np.max(time[:]) for time in times]))
        self.time_width = self.time_span[1] - self.time_span[0]

        self.ax_traj.set_xlim((self.x_span[0]-self.x_width*self.EXTRA_WIDTH_TRAJ,
                               self.x_span[1]+self.x_width*self.EXTRA_WIDTH_TRAJ))
        self.ax_traj.set_ylim((self.y_span[0]-self.y_width*self.EXTRA_WIDTH_TRAJ,
                               self.y_span[1]+self.y_width*self.EXTRA_WIDTH_TRAJ))

        self.ax_dyn.set_xlim((self.x_span[0]-self.x_width*self.EXTRA_WIDTH_DYN,
                               self.x_span[1]+self.x_width*self.EXTRA_WIDTH_DYN))
        self.ax_dyn.set_ylim((self.y_span[0]-self.y_width*self.EXTRA_WIDTH_DYN,
                               self.y_span[1]+self.y_width*self.EXTRA_WIDTH_DYN))

        for ix, ax in enumerate(self.axes_traj_split.flatten()):
            ax.set_xlim((self.time_span[0]-self.time_width*self.EXTRA_WIDTH_TRAJ,
                         self.time_span[1]+self.time_width*self.EXTRA_WIDTH_TRAJ))
            if ix == 0:
                ax.set_ylim((self.x_span[0]-self.x_width*self.EXTRA_WIDTH_TRAJ,
                             self.x_span[1]+self.x_width*self.EXTRA_WIDTH_TRAJ))
            elif ix == 1:
                ax.set_ylim((self.y_span[0]-self.y_width*self.EXTRA_WIDTH_TRAJ,
                             self.y_span[1]+self.y_width*self.EXTRA_WIDTH_TRAJ))    
            elif ix == 2:
                ax.set_ylim((self.xdot_span[0]-self.xdot_width*self.EXTRA_WIDTH_TRAJ,
                             self.xdot_span[1]+self.xdot_width*self.EXTRA_WIDTH_TRAJ))
            elif ix == 3:
                ax.set_ylim((self.ydot_span[0]-self.ydot_width*self.EXTRA_WIDTH_TRAJ,
                             self.ydot_span[1]+self.ydot_width*self.EXTRA_WIDTH_TRAJ))

    def visualize(self):
        self.trajectories = self.data_handler.calculate_trajectory(self.odenet, self.settings['method'])
        self._visualize_trajectories_all()
        self._visualize_trajectories_split()
        self._visualize_dynamics()
        self._set_ax_limits()

    def _visualize_trajectories_all(self):
        self.ax_traj.cla()

        for j in range(self.data_handler.ntraj-1, -1, -1):
            self.ax_traj.plot(self.data_handler.data_np[j][:,:,0].flatten(), self.data_handler.data_np[j][:,:,1].flatten(), 'r-o', alpha=0.3)

        
        for j in range(self.data_handler.ntraj):
            self.ax_traj.plot(self.trajectories[j][:,:,0].numpy().flatten(), self.trajectories[j][:,:,1].numpy().flatten(), 'k--', lw=2)

        
        self.ax_traj.set_xlabel(r'$x$')
        self.ax_traj.set_ylabel(r'$y$')
        self.ax_traj.legend(handles=self.legend_traj, loc='upper center', ncol=2)

    def _visualize_trajectories_split(self):
        times = self.data_handler.time_np

        for i, ax in enumerate(self.axes_traj_split.flatten()):
            ax.cla()
            for j, (approx_traj, traj) in enumerate(zip(self.trajectories, self.data_handler.data_np)):
                ax.plot(times[j].flatten(), traj[:,:,i].flatten(), 'r-o', alpha=0.3)
                ax.plot(times[j].flatten(), approx_traj[:,:,i].numpy().flatten(),'k--', lw=2)
            ax.set_xlabel(r'$t$')
            if i == 0:
                ax.set_ylabel(r'$x$')
            elif i == 1:
                ax.set_ylabel(r'$y$')
            elif i == 2:
                ax.set_ylabel(r'$\dot{x}$')
            elif i == 3:
                ax.set_ylabel(r'$\dot{y}$')

    def _visualize_dynamics(self):
        GRIDSIZE = 20

        self.ax_dyn.cla()
        for j in range(self.data_handler.ntraj-1, -1, -1):
            self.ax_dyn.plot(self.data_handler.data_np[j][:,:,0].flatten(), self.data_handler.data_np[j][:,:,1].flatten(), '-r', alpha=0.3, linewidth=2)

        xv, yv, xdotv, ydotv = torch.meshgrid([torch.linspace(self.x_span[0]-self.x_width*self.EXTRA_WIDTH_DYN, 
                                                self.x_span[1]+self.x_width*self.EXTRA_WIDTH_DYN, 
                                                GRIDSIZE),
                                               torch.linspace(self.y_span[0]-self.y_width*self.EXTRA_WIDTH_DYN, 
                                                self.y_span[1]+self.y_width*self.EXTRA_WIDTH_DYN, 
                                                GRIDSIZE),
                                               torch.linspace(self.xdot_span[0]-self.xdot_width*self.EXTRA_WIDTH_DYN,
                                                self.xdot_span[1]+self.xdot_width*self.EXTRA_WIDTH_DYN, 
                                                GRIDSIZE),
                                               torch.linspace(self.ydot_span[0]-self.ydot_width*self.EXTRA_WIDTH_DYN,
                                                self.ydot_span[1]+self.ydot_width*self.EXTRA_WIDTH_DYN, 
                                                GRIDSIZE)])
        inputs = torch.from_numpy(np.vstack([array for array in map(np.ravel, (xv, yv, xdotv, ydotv))])).to(self.data_handler.device)
        inputs = torch.transpose(inputs, 1, 0)
        t = torch.zeros(1).to(self.data_handler.device)
        grad = self.odenet.forward(t, inputs)
        grad_x = grad[:, 0].reshape(xv.shape).cpu().numpy()
        grad_y = grad[:, 1].reshape(yv.shape).cpu().numpy()
        grad_xdot = grad[:, 2].reshape(xdotv.shape).cpu().numpy()
        grad_ydot = grad[:, 3].reshape(ydotv.shape).cpu().numpy()

        self.ax_dyn.quiver(xv[:,:,0,0], yv[:,:,0,0], grad_x[:,:,0,0], grad_y[:,:,0,0])
        self.ax_dyn.set_xlabel(r'$x$')
        self.ax_dyn.set_ylabel(r'$y$')
        self.ax_dyn.legend(handles=self.legend_traj, loc='upper center', ncol=2)

    def save(self, dir, epoch):
         self.fig_dyn.savefig('{}dyn_epoch{}.eps'.format(dir, epoch))
         self.fig_traj.savefig('{}traj_epoch{}.eps'.format(dir, epoch))
         self.fig_traj_split.savefig('{}each_dim_epoch{}.eps'.format(dir, epoch))
         self.fig_dyn.savefig('{}dyn_epoch{}.png'.format(dir, epoch))
         self.fig_traj.savefig('{}traj_epoch{}.png'.format(dir, epoch))
         self.fig_traj_split.savefig('{}each_dim_epoch{}.png'.format(dir, epoch))

class VisualizatorMystery(Visualizator):
    
    def __init__(self, data_handler, odenet, settings):
        super().__init__(data_handler, odenet, settings)
        self.fig_dyn = plt.figure(figsize=(6,6))
        self.fig_dyn.canvas.set_window_title("Dynamics")
        self.ax_dyn = self.fig_dyn.add_subplot(111, frameon=False)
        self.fig_traj = plt.figure(figsize=(6,6))
        self.fig_traj.canvas.set_window_title("Trajectories")
        self.ax_traj = self.fig_traj.add_subplot(111, frameon=False)
        self.fig_traj_split = plt.figure(figsize=(12,6))
        self.fig_traj_split.canvas.set_window_title("Trajectories in each dimension")
        self.axes_traj_split = self.fig_traj_split.subplots(nrows=2, ncols=2, sharex=False, subplot_kw={'frameon':True})

        self.legend_traj = [Line2D([0], [0], color='black', linestyle='--', label='NN approximation'),
                Line2D([0], [0], marker='o', color='red', label='Data', markerfacecolor='red', markersize=5)]

        self.fig_traj_split.legend(handles=self.legend_traj, loc='upper center', ncol=2)
        
        self._set_ax_limits()

        plt.show(block=True)
        
    def plot(self):
        #plt.figure(1)
        self.fig_dyn.canvas.draw_idle()
        self.fig_dyn.canvas.start_event_loop(0.005)
        #plt.figure(2)
        self.fig_traj.canvas.draw_idle()
        self.fig_traj.canvas.start_event_loop(0.005)

        self.fig_traj_split.canvas.draw_idle()
        self.fig_traj_split.canvas.start_event_loop(0.005)

    def _set_ax_limits(self):
        data = self.data_handler.data_np
        times = self.data_handler.time_np
        self.EXTRA_WIDTH_TRAJ = 0.2
        self.EXTRA_WIDTH_DYN = 1

        self.x_span = (np.min([np.min(traj[:,:,0]) for traj in data]),
                       np.max([np.max(traj[:,:,0]) for traj in data]))
        self.x_width = self.x_span[1] - self.x_span[0]


        self.y_span = (np.min([np.min(traj[:,:,1]) for traj in data]),
                       np.max([np.max(traj[:,:,1]) for traj in data]))
        self.y_width = self.y_span[1] - self.y_span[0]

        self.xdot_span = (np.min([np.min(traj[:,:,2]) for traj in data]),
                          np.max([np.max(traj[:,:,2]) for traj in data]))
        self.xdot_width = self.xdot_span[1] - self.xdot_span[0]

        self.ydot_span = (np.min([np.min(traj[:,:,3]) for traj in data]),
                          np.max([np.max(traj[:,:,3]) for traj in data]))
        self.ydot_width = self.ydot_span[1] - self.ydot_span[0]

        
        self.time_span = (np.min([np.min(time[:]) for time in times]),
                          np.max([np.max(time[:]) for time in times]))
        self.time_width = self.time_span[1] - self.time_span[0]

        self.ax_traj.set_xlim((self.x_span[0]-self.x_width*self.EXTRA_WIDTH_TRAJ,
                               self.x_span[1]+self.x_width*self.EXTRA_WIDTH_TRAJ))
        self.ax_traj.set_ylim((self.y_span[0]-self.y_width*self.EXTRA_WIDTH_TRAJ,
                               self.y_span[1]+self.y_width*self.EXTRA_WIDTH_TRAJ))

        self.ax_dyn.set_xlim((self.x_span[0]-self.x_width*self.EXTRA_WIDTH_DYN,
                               self.x_span[1]+self.x_width*self.EXTRA_WIDTH_DYN))
        self.ax_dyn.set_ylim((self.y_span[0]-self.y_width*self.EXTRA_WIDTH_DYN,
                               self.y_span[1]+self.y_width*self.EXTRA_WIDTH_DYN))

        for ix, ax in enumerate(self.axes_traj_split.flatten()):
            ax.set_xlim((self.time_span[0]-self.time_width*self.EXTRA_WIDTH_TRAJ,
                         self.time_span[1]+self.time_width*self.EXTRA_WIDTH_TRAJ))
            if ix == 0:
                ax.set_ylim((self.x_span[0]-self.x_width*self.EXTRA_WIDTH_TRAJ,
                             self.x_span[1]+self.x_width*self.EXTRA_WIDTH_TRAJ))
            elif ix == 1:
                ax.set_ylim((self.y_span[0]-self.y_width*self.EXTRA_WIDTH_TRAJ,
                             self.y_span[1]+self.y_width*self.EXTRA_WIDTH_TRAJ))    
            elif ix == 2:
                ax.set_ylim((self.xdot_span[0]-self.xdot_width*self.EXTRA_WIDTH_TRAJ,
                             self.xdot_span[1]+self.xdot_width*self.EXTRA_WIDTH_TRAJ))
            elif ix == 3:
                ax.set_ylim((self.ydot_span[0]-self.ydot_width*self.EXTRA_WIDTH_TRAJ,
                             self.ydot_span[1]+self.ydot_width*self.EXTRA_WIDTH_TRAJ))

    def visualize(self):
        self.trajectories = self.data_handler.calculate_trajectory(self.odenet, self.settings['method'])
        self._visualize_trajectories_all()
        self._visualize_trajectories_split()
        #self._visualize_dynamics()
        self._set_ax_limits()

    def _visualize_trajectories_all(self):
        self.ax_traj.cla()

        for j in range(self.data_handler.ntraj-1, -1, -1):
            self.ax_traj.plot(self.data_handler.data_np[j][:,:,0].flatten(), self.data_handler.data_np[j][:,:,1].flatten(), 'r-o', alpha=0.3)

        
        for j in range(self.data_handler.ntraj):
            self.ax_traj.plot(self.trajectories[j][:,:,0].numpy().flatten(), self.trajectories[j][:,:,1].numpy().flatten(), 'k--', lw=2)

        
        self.ax_traj.set_xlabel(r'$x$')
        self.ax_traj.set_ylabel(r'$y$')
        self.ax_traj.legend(handles=self.legend_traj, loc='upper center', ncol=2)

    def _visualize_trajectories_split(self):
        times = self.data_handler.time_np

        for i, ax in enumerate(self.axes_traj_split.flatten()):
            ax.cla()
            for j, (approx_traj, traj) in enumerate(zip(self.trajectories, self.data_handler.data_np)):
                ax.plot(times[j].flatten(), traj[:,:,i].flatten(), 'r-o', alpha=0.3)
                ax.plot(times[j].flatten(), approx_traj[:,:,i].numpy().flatten(),'k--', lw=2)
            ax.set_xlabel(r'$t$')
            if i == 0:
                ax.set_ylabel(r'$x$')
            elif i == 1:
                ax.set_ylabel(r'$y$')
            elif i == 2:
                ax.set_ylabel(r'$\dot{x}$')
            elif i == 3:
                ax.set_ylabel(r'$\dot{y}$')

    def _visualize_dynamics(self):
        GRIDSIZE = 20

        self.ax_dyn.cla()
        for j in range(self.data_handler.ntraj-1, -1, -1):
            self.ax_dyn.plot(self.data_handler.data_np[j][:,:,0].flatten(), self.data_handler.data_np[j][:,:,1].flatten(), '-r', alpha=0.3, linewidth=2)

        xv, yv, xdotv, ydotv = torch.meshgrid([torch.linspace(self.x_span[0]-self.x_width*self.EXTRA_WIDTH_DYN, 
                                                self.x_span[1]+self.x_width*self.EXTRA_WIDTH_DYN, 
                                                GRIDSIZE),
                                               torch.linspace(self.y_span[0]-self.y_width*self.EXTRA_WIDTH_DYN, 
                                                self.y_span[1]+self.y_width*self.EXTRA_WIDTH_DYN, 
                                                GRIDSIZE),
                                               torch.linspace(self.xdot_span[0]-self.xdot_width*self.EXTRA_WIDTH_DYN,
                                                self.xdot_span[1]+self.xdot_width*self.EXTRA_WIDTH_DYN, 
                                                GRIDSIZE),
                                               torch.linspace(self.ydot_span[0]-self.ydot_width*self.EXTRA_WIDTH_DYN,
                                                self.ydot_span[1]+self.ydot_width*self.EXTRA_WIDTH_DYN, 
                                                GRIDSIZE)])
        inputs = torch.from_numpy(np.vstack([array for array in map(np.ravel, (xv, yv, xdotv, ydotv))])).to(self.data_handler.device)
        inputs = torch.transpose(inputs, 1, 0)
        t = torch.zeros(inputs.shape[0]).to(self.data_handler.device)
        grad = self.odenet.forward(t, inputs)
        grad_x = grad[:, 0].reshape(xv.shape).cpu().numpy()
        grad_y = grad[:, 1].reshape(yv.shape).cpu().numpy()
        grad_xdot = grad[:, 2].reshape(xdotv.shape).cpu().numpy()
        grad_ydot = grad[:, 3].reshape(ydotv.shape).cpu().numpy()

        self.ax_dyn.quiver(xv[:,:,0,0], yv[:,:,0,0], grad_x[:,:,0,0], grad_y[:,:,0,0])
        self.ax_dyn.set_xlabel(r'$x$')
        self.ax_dyn.set_ylabel(r'$y$')
        self.ax_dyn.legend(handles=self.legend_traj, loc='upper center', ncol=2)

    def save(self, dir, epoch):
         #self.fig_dyn.savefig('{}dyn_epoch{}.eps'.format(dir, epoch))
         self.fig_traj.savefig('{}traj_epoch{}.eps'.format(dir, epoch))
         self.fig_traj_split.savefig('{}each_dim_epoch{}.eps'.format(dir, epoch))
         self.fig_traj.savefig('{}traj_epoch{}.png'.format(dir, epoch))
         self.fig_traj_split.savefig('{}each_dim_epoch{}.png'.format(dir, epoch))


class Visualizator1DTimeDependent(Visualizator):
    
    def __init__(self, data_handler, odenet, settings):
        super().__init__(data_handler, odenet, settings)
        self.fig_dyn = plt.figure(figsize=(6,6))
        self.fig_dyn.canvas.set_window_title("Dynamics")
        self.ax_dyn = self.fig_dyn.add_subplot(111, frameon=False)
        self.fig_traj = plt.figure(figsize=(6,6))
        self.fig_traj.canvas.set_window_title("Trajectories")
        self.ax_traj = self.fig_traj.add_subplot(111, frameon=False)
        self.fig_traj_split = plt.figure(figsize=(12,4))
        self.fig_traj_split.canvas.set_window_title("Trajectories in each dimension")
        self.axes_traj_split = self.fig_traj_split.subplots(nrows=1, ncols=2, sharex=False, subplot_kw={'frameon':True})

        self.legend_traj = [Line2D([0], [0], color='black', linestyle='--', label='NN approximation'),
                Line2D([0], [0], marker='o', color='red', label='Data', markerfacecolor='red', markersize=5)]

        self.fig_traj_split.legend(handles=self.legend_traj, loc='upper center', ncol=2)
        
        self._set_ax_limits()

        plt.show(block=True)
        
    def plot(self):
        #plt.figure(1)
        self.fig_dyn.canvas.draw_idle()
        self.fig_dyn.canvas.start_event_loop(0.005)
        #plt.figure(2)
        self.fig_traj.canvas.draw_idle()
        self.fig_traj.canvas.start_event_loop(0.005)

        self.fig_traj_split.canvas.draw_idle()
        self.fig_traj_split.canvas.start_event_loop(0.005)

    def _set_ax_limits(self):
        data = self.data_handler.data_np
        times = self.data_handler.time_np
        self.EXTRA_WIDTH_TRAJ = 0.2
        self.EXTRA_WIDTH_DYN = 1

        self.x_span = (np.min([np.min(traj[:,:,0]) for traj in data]),
                       np.max([np.max(traj[:,:,0]) for traj in data]))
        self.x_width = self.x_span[1] - self.x_span[0]

        self.xdot_span = (np.min([np.min(traj[:,:,1]) for traj in data]),
                          np.max([np.max(traj[:,:,1]) for traj in data]))
        self.xdot_width = self.xdot_span[1] - self.xdot_span[0]

        self.time_span = (np.min([np.min(time[:]) for time in times]),
                          np.max([np.max(time[:]) for time in times]))
        self.time_width = self.time_span[1] - self.time_span[0]

        self.ax_traj.set_xlim((self.x_span[0]-self.x_width*self.EXTRA_WIDTH_TRAJ,
                               self.x_span[1]+self.x_width*self.EXTRA_WIDTH_TRAJ))
        self.ax_traj.set_ylim((self.xdot_span[0]-self.xdot_width*self.EXTRA_WIDTH_TRAJ,
                               self.xdot_span[1]+self.xdot_width*self.EXTRA_WIDTH_TRAJ))

        self.ax_dyn.set_xlim((self.x_span[0]-self.x_width*self.EXTRA_WIDTH_DYN,
                               self.x_span[1]+self.x_width*self.EXTRA_WIDTH_DYN))
        self.ax_dyn.set_ylim((self.xdot_span[0]-self.xdot_width*self.EXTRA_WIDTH_DYN,
                               self.xdot_span[1]+self.xdot_width*self.EXTRA_WIDTH_DYN))

        for ix, ax in enumerate(self.axes_traj_split):
            ax.set_xlim((self.time_span[0]-self.time_width*self.EXTRA_WIDTH_TRAJ,
                         self.time_span[1]+self.time_width*self.EXTRA_WIDTH_TRAJ))
            if ix == 0:
                ax.set_ylim((self.x_span[0]-self.x_width*self.EXTRA_WIDTH_TRAJ,
                             self.x_span[1]+self.x_width*self.EXTRA_WIDTH_TRAJ))
            if ix == 1:
                ax.set_ylim((self.xdot_span[0]-self.xdot_width*self.EXTRA_WIDTH_TRAJ,
                             self.xdot_span[1]+self.xdot_width*self.EXTRA_WIDTH_TRAJ))

    def visualize(self):
        self.trajectories = self.data_handler.calculate_trajectory(self.odenet, self.settings['method'])
        self._visualize_trajectories_all()
        self._visualize_trajectories_split()
        #self._visualize_dynamics()
        self._set_ax_limits()

    def _visualize_trajectories_all(self):
        self.ax_traj.cla()

        for j in range(self.data_handler.ntraj-1, -1, -1):
            self.ax_traj.plot(self.data_handler.data_np[j][:,:,0].flatten(), self.data_handler.data_np[j][:,:,1].flatten(), 'r-o', alpha=0.3)

        
        for j in range(self.data_handler.ntraj):
            self.ax_traj.plot(self.trajectories[j][:,:,0].numpy().flatten(), self.trajectories[j][:,:,1].numpy().flatten(), 'k--', lw=2)

        
        self.ax_traj.set_xlabel(r'$x_0$ [m]')
        self.ax_traj.set_ylabel(r'$x_1$ [m]')
        self.ax_traj.legend(handles=self.legend_traj, loc='upper center', ncol=2)

    def _visualize_trajectories_split(self):
        times = self.data_handler.time_np

        for i, ax in enumerate(self.axes_traj_split):
            ax.cla()
            for j, (approx_traj, traj) in enumerate(zip(self.trajectories, self.data_handler.data_np)):
                ax.plot(times[j].flatten(), traj[:,:,i].flatten(), 'r-o', alpha=0.3)
                ax.plot(times[j].flatten(), approx_traj[:,:,i].numpy().flatten(),'k--', lw=2)
            ax.set_xlabel(r'$t$ [s]')
            if i == 0:
                ax.set_ylabel(r'$x_0$ [m]')
            elif i == 1:
                ax.set_ylabel(r'$x_1$ [m]')

    def _visualize_dynamics(self):
        GRIDSIZE = 20

        self.ax_dyn.cla()
        for j in range(self.data_handler.ntraj-1, -1, -1):
            self.ax_dyn.plot(self.data_handler.data_np[j][:,:,0].flatten(), self.data_handler.data_np[j][:,:,1].flatten(), '-r', alpha=0.3, linewidth=2)

        xv, yv = torch.meshgrid([torch.linspace(self.x_span[0]-self.x_width*self.EXTRA_WIDTH_DYN, 
                                                self.x_span[1]+self.x_width*self.EXTRA_WIDTH_DYN, 
                                                GRIDSIZE),
                                 torch.linspace(self.xdot_span[0]-self.xdot_width*self.EXTRA_WIDTH_DYN,
                                                self.xdot_span[1]+self.xdot_width*self.EXTRA_WIDTH_DYN, 
                                                GRIDSIZE)])
        inputs = torch.from_numpy(np.vstack([array for array in map(np.ravel, (xv, yv))])).to(self.data_handler.device)
        inputs = torch.transpose(inputs, 1, 0)
        t = torch.zeros(1).to(self.data_handler.device)
        grad = self.odenet.forward(t, inputs)
        grad_x = grad[:, 0].reshape(xv.shape).cpu().numpy()
        grad_y = grad[:, 1].reshape(yv.shape).cpu().numpy()

        self.ax_dyn.quiver(xv, yv, grad_x, grad_y)
        self.ax_dyn.set_xlabel(r'$x$')
        self.ax_dyn.set_ylabel(r'$\dot{x}$')
        self.ax_dyn.legend(handles=self.legend_traj, loc='upper center', ncol=2)

    def save(self, dir, epoch):
         #self.fig_dyn.savefig('{}dyn_epoch{}.eps'.format(dir, epoch))
         self.fig_traj.savefig('{}traj_epoch{}.eps'.format(dir, epoch))
         self.fig_traj_split.savefig('{}each_dim_epoch{}.eps'.format(dir, epoch))
         self.fig_traj.savefig('{}traj_epoch{}.png'.format(dir, epoch))
         self.fig_traj_split.savefig('{}each_dim_epoch{}.png'.format(dir, epoch))

class Visualizator2DTimeDependent(Visualizator):
    
    def __init__(self, data_handler, odenet, settings):
        super().__init__(data_handler, odenet, settings)
        self.fig_dyn = plt.figure(figsize=(6,6))
        self.fig_dyn.canvas.set_window_title("Dynamics")
        self.ax_dyn = self.fig_dyn.add_subplot(111, frameon=False)
        self.fig_traj = plt.figure(figsize=(6,6))
        self.fig_traj.canvas.set_window_title("Trajectories")
        self.ax_traj = self.fig_traj.add_subplot(111, frameon=False)
        self.fig_traj_split = plt.figure(figsize=(12,6))
        self.fig_traj_split.canvas.set_window_title("Trajectories in each dimension")
        self.axes_traj_split = self.fig_traj_split.subplots(nrows=2, ncols=2, sharex=False, subplot_kw={'frameon':True})

        self.legend_traj = [Line2D([0], [0], color='black', linestyle='--', label='NN approximation'),
                Line2D([0], [0], marker='o', color='red', label='Data', markerfacecolor='red', markersize=5)]

        self.fig_traj_split.legend(handles=self.legend_traj, loc='upper center', ncol=2)
        
        self._set_ax_limits()

        plt.show(block=True)
        
    def plot(self):
        #plt.figure(1)
        self.fig_dyn.canvas.draw_idle()
        self.fig_dyn.canvas.start_event_loop(0.005)
        #plt.figure(2)
        self.fig_traj.canvas.draw_idle()
        self.fig_traj.canvas.start_event_loop(0.005)

        self.fig_traj_split.canvas.draw_idle()
        self.fig_traj_split.canvas.start_event_loop(0.005)

    def _set_ax_limits(self):
        data = self.data_handler.data_np
        times = self.data_handler.time_np
        self.EXTRA_WIDTH_TRAJ = 0.2
        self.EXTRA_WIDTH_DYN = 1

        self.x_span = (np.min([np.min(traj[:,:,0]) for traj in data]),
                       np.max([np.max(traj[:,:,0]) for traj in data]))
        self.x_width = self.x_span[1] - self.x_span[0]


        self.y_span = (np.min([np.min(traj[:,:,1]) for traj in data]),
                       np.max([np.max(traj[:,:,1]) for traj in data]))
        self.y_width = self.y_span[1] - self.y_span[0]

        self.xdot_span = (np.min([np.min(traj[:,:,2]) for traj in data]),
                          np.max([np.max(traj[:,:,2]) for traj in data]))
        self.xdot_width = self.xdot_span[1] - self.xdot_span[0]

        self.ydot_span = (np.min([np.min(traj[:,:,3]) for traj in data]),
                          np.max([np.max(traj[:,:,3]) for traj in data]))
        self.ydot_width = self.ydot_span[1] - self.ydot_span[0]

        
        self.time_span = (np.min([np.min(time[:]) for time in times]),
                          np.max([np.max(time[:]) for time in times]))
        self.time_width = self.time_span[1] - self.time_span[0]

        self.ax_traj.set_xlim((self.x_span[0]-self.x_width*self.EXTRA_WIDTH_TRAJ,
                               self.x_span[1]+self.x_width*self.EXTRA_WIDTH_TRAJ))
        self.ax_traj.set_ylim((self.y_span[0]-self.y_width*self.EXTRA_WIDTH_TRAJ,
                               self.y_span[1]+self.y_width*self.EXTRA_WIDTH_TRAJ))

        self.ax_dyn.set_xlim((self.x_span[0]-self.x_width*self.EXTRA_WIDTH_DYN,
                               self.x_span[1]+self.x_width*self.EXTRA_WIDTH_DYN))
        self.ax_dyn.set_ylim((self.y_span[0]-self.y_width*self.EXTRA_WIDTH_DYN,
                               self.y_span[1]+self.y_width*self.EXTRA_WIDTH_DYN))

        for ix, ax in enumerate(self.axes_traj_split.flatten()):
            ax.set_xlim((self.time_span[0]-self.time_width*self.EXTRA_WIDTH_TRAJ,
                         self.time_span[1]+self.time_width*self.EXTRA_WIDTH_TRAJ))
            if ix == 0:
                ax.set_ylim((self.x_span[0]-self.x_width*self.EXTRA_WIDTH_TRAJ,
                             self.x_span[1]+self.x_width*self.EXTRA_WIDTH_TRAJ))
            elif ix == 1:
                ax.set_ylim((self.y_span[0]-self.y_width*self.EXTRA_WIDTH_TRAJ,
                             self.y_span[1]+self.y_width*self.EXTRA_WIDTH_TRAJ))    
            elif ix == 2:
                ax.set_ylim((self.xdot_span[0]-self.xdot_width*self.EXTRA_WIDTH_TRAJ,
                             self.xdot_span[1]+self.xdot_width*self.EXTRA_WIDTH_TRAJ))
            elif ix == 3:
                ax.set_ylim((self.ydot_span[0]-self.ydot_width*self.EXTRA_WIDTH_TRAJ,
                             self.ydot_span[1]+self.ydot_width*self.EXTRA_WIDTH_TRAJ))

    def visualize(self):
        self.trajectories = self.data_handler.calculate_trajectory(self.odenet, self.settings['method'])
        #self._visualize_trajectories_all()
        self._visualize_trajectories_split()
        #self._visualize_dynamics()
        self._set_ax_limits()

    def _visualize_trajectories_all(self):
        self.ax_traj.cla()

        for j in range(self.data_handler.ntraj-1, -1, -1):
            self.ax_traj.plot(self.data_handler.data_np[j][:,:,0].flatten(), self.data_handler.data_np[j][:,:,1].flatten(), 'r-o', alpha=0.3)

        
        for j in range(self.data_handler.ntraj):
            self.ax_traj.plot(self.trajectories[j][:,:,0].numpy().flatten(), self.trajectories[j][:,:,1].numpy().flatten(), 'k--', lw=2)

        
        self.ax_traj.set_xlabel(r'$x$')
        self.ax_traj.set_ylabel(r'$y$')
        self.ax_traj.legend(handles=self.legend_traj, loc='upper center', ncol=2)

    def _visualize_trajectories_split(self):
        times = self.data_handler.time_np

        for i, ax in enumerate(self.axes_traj_split.flatten()):
            ax.cla()
            for j, (approx_traj, traj) in enumerate(zip(self.trajectories, self.data_handler.data_np)):
                ax.plot(times[j].flatten(), traj[:,:,i].flatten(), 'r-o', alpha=0.3)
                ax.plot(times[j].flatten(), approx_traj[:,:,i].numpy().flatten(),'k--', lw=2)
            ax.set_xlabel(r'$t$ [s]')
            if i == 0:
                ax.set_ylabel(r'$x_0$ [m]')
            elif i == 1:
                ax.set_ylabel(r'$\frac{\mathrm{d}x_0}{\mathrm{d}t}$ [m s$^{-1}$]')
            elif i == 2:
                ax.set_ylabel(r'$x_1$ [m]')
            elif i == 3:
                ax.set_ylabel(r'$\frac{\mathrm{d}x_1}{\mathrm{d}t}$ [m s$^{-1}$]')

    def _visualize_dynamics(self):
        GRIDSIZE = 20

        self.ax_dyn.cla()
        for j in range(self.data_handler.ntraj-1, -1, -1):
            self.ax_dyn.plot(self.data_handler.data_np[j][:,:,0].flatten(), self.data_handler.data_np[j][:,:,1].flatten(), '-r', alpha=0.3, linewidth=2)

        xv, yv, xdotv, ydotv = torch.meshgrid([torch.linspace(self.x_span[0]-self.x_width*self.EXTRA_WIDTH_DYN, 
                                                self.x_span[1]+self.x_width*self.EXTRA_WIDTH_DYN, 
                                                GRIDSIZE),
                                               torch.linspace(self.y_span[0]-self.y_width*self.EXTRA_WIDTH_DYN, 
                                                self.y_span[1]+self.y_width*self.EXTRA_WIDTH_DYN, 
                                                GRIDSIZE),
                                               torch.linspace(self.xdot_span[0]-self.xdot_width*self.EXTRA_WIDTH_DYN,
                                                self.xdot_span[1]+self.xdot_width*self.EXTRA_WIDTH_DYN, 
                                                GRIDSIZE),
                                               torch.linspace(self.ydot_span[0]-self.ydot_width*self.EXTRA_WIDTH_DYN,
                                                self.ydot_span[1]+self.ydot_width*self.EXTRA_WIDTH_DYN, 
                                                GRIDSIZE)])
        inputs = torch.from_numpy(np.vstack([array for array in map(np.ravel, (xv, yv, xdotv, ydotv))])).to(self.data_handler.device)
        inputs = torch.transpose(inputs, 1, 0)
        t = torch.zeros(1).to(self.data_handler.device)
        grad = self.odenet.forward(t, inputs)
        grad_x = grad[:, 0].reshape(xv.shape).cpu().numpy()
        grad_y = grad[:, 1].reshape(yv.shape).cpu().numpy()
        grad_xdot = grad[:, 2].reshape(xdotv.shape).cpu().numpy()
        grad_ydot = grad[:, 3].reshape(ydotv.shape).cpu().numpy()

        self.ax_dyn.quiver(xv[:,:,0,0], yv[:,:,0,0], grad_x[:,:,0,0], grad_y[:,:,0,0])
        self.ax_dyn.set_xlabel(r'$x$')
        self.ax_dyn.set_ylabel(r'$y$')
        self.ax_dyn.legend(handles=self.legend_traj, loc='upper center', ncol=2)

    def save(self, dir, epoch):
         self.fig_dyn.savefig('{}dyn_epoch{}.eps'.format(dir, epoch))
         self.fig_traj.savefig('{}traj_epoch{}.eps'.format(dir, epoch))
         self.fig_traj_split.savefig('{}each_dim_epoch{}.eps'.format(dir, epoch))
         self.fig_dyn.savefig('{}dyn_epoch{}.png'.format(dir, epoch))
         self.fig_traj.savefig('{}traj_epoch{}.png'.format(dir, epoch))
         self.fig_traj_split.savefig('{}each_dim_epoch{}.png'.format(dir, epoch))